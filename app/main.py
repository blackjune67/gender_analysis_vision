from fastapi import FastAPI
from app.api.websocket import router
import tensorflow as tf
import os

app = FastAPI(
    title="Gender Detection API",
    description="웹소켓을 통해 비디오 스트림에서 성별을 감지하는 API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 경로
    redoc_url="/redoc"  # ReDoc 경로
)

def limit_memory():
    # CPU 메모리 사용량 제한
    try:
        # 물리적 메모리의 약 50%로 제한
        physical_devices = tf.config.list_physical_devices('CPU')
        if physical_devices:
            # CPU 스레드 제한
            tf.config.threading.set_intra_op_parallelism_threads(1)
            tf.config.threading.set_inter_op_parallelism_threads(1)

        # 텐서플로우 메모리 성장 제한
        tf.config.set_soft_device_placement(True)
        
        # 환경 변수로 메모리 제한
        os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 경고 메시지 줄이기
        
        # 메모리 분수 설정 (전체 메모리의 50%만 사용)
        memory_limit = int(0.5 * 1024 * 1024 * 1024)  # 0.5GB
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                    tf.config.experimental.set_virtual_device_configuration(
                        gpu,
                        [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=memory_limit)]
                    )
            except RuntimeError as e:
                print(f"GPU 설정 중 오류 발생: {e}")
                
    except Exception as e:
        print(f"메모리 제한 설정 중 오류 발생: {e}")
        
# 메모리 제한 적용
limit_memory()

# API 컨트롤러
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)