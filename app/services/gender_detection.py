from deepface import DeepFace
from logging_loki import LokiHandler
from time import time
import cv2
import numpy as np
import logging
import traceback

# 로그 설정
loki_handler = LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"application": "gender_analysis_vision"},
    version="1",
)

# 파일 핸들러 추가
# file_handler = logging.FileHandler('gender_detection.log')
# file_handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)  # 로깅 레벨을 DEBUG로 변경
# logger.addHandler(loki_handler)
# logger.addHandler(file_handler)

class FrameProcessor:
    def __init__(self, frame_interval=5):
        self.frame_count = 0
        self.frame_interval = frame_interval
        self.last_process_time = time()
        self.fps = 24
        self.min_process_interval = 1.0 / (self.fps / self.frame_interval)
        self.error_count = 0  # 에러 카운트 추가
        
    def should_process_frame(self):
        current_time = time()
        time_elapsed = current_time - self.last_process_time
        
        self.frame_count += 1
        
        if (self.frame_count % self.frame_interval == 0) and (time_elapsed >= self.min_process_interval):
            self.last_process_time = current_time
            return True
        return False

def process_frame(data, frame_processor):
    """
    ### 프레임 처리
    - **기능**: 수신된 비디오 스트림 데이터를 분석해 성별 정보를 추출합니다.
    - **입력 데이터**: 바이너리 형태의 비디오 프레임
    - **출력 데이터**:
        - 성별 (`gender`): "남성" 또는 "여성"
        - 나이 (`age`): 추정된 나이
        - 신뢰도 (`confidence`): 0.0 ~ 1.0 사이의 값
    """
    try:
        if not frame_processor.should_process_frame():
            return None

        logging.debug(f"프레임 처리 중: {frame_processor.frame_count} (매 {frame_processor.frame_interval} 프레임마다 처리)")

        # 이미지 디코딩 시도
        try:
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                raise ValueError("이미지 데이터 디코딩 실패")
        except Exception as e:
            logging.error(f"이미지 디코딩 오류: {str(e)}")
            return None

        result_list = []
        
        try:
            analysis = DeepFace.analyze(
                frame,
                actions=['age','gender'],
                enforce_detection=False,
                detector_backend='opencv' # mtcnn, retinaface, yolo 등을 사용할 수 있음.
            )

             # 리스트가 아닌 경우 리스트로 변환
            if not isinstance(analysis, list):
                analysis = [analysis]

            for face_data in analysis:
                try:
                    gender = "남성" if face_data["gender"]["Man"] > face_data["gender"]["Woman"] else "여성"
                    gender_confidence = max(face_data["gender"]["Man"], face_data["gender"]["Woman"]) / 100.0
                    age = face_data["age"]

                    result_list.append({
                        "gender": gender,
                        "age": age,
                        "confidence": gender_confidence
                    })

                    logging.info(f"[프레임 {frame_processor.frame_count}] "
                               f"인식 결과: {gender}, 나이: {age}, 정확도: {gender_confidence:.2f}")
                
                except Exception as e:
                    logging.error(f"얼굴 데이터 처리 중 오류: {str(e)}")
                    continue

        except Exception as e:
            logging.error(f"DeepFace 분석 중 오류: {str(e)}")
            return None

        return result_list

    except Exception as e:
        error_traceback = traceback.format_exc()
        logging.error(f"프레임 처리 중 심각한 오류 발생:\n{error_traceback}")
        frame_processor.error_count += 1
        
        # 연속적인 에러 발생 시 로깅
        if frame_processor.error_count > 5:
            logging.critical(f"연속적인 오류 발생 감지됨: {frame_processor.error_count}회")
        
        return None