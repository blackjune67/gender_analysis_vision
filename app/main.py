from fastapi import FastAPI
from app.api.websocket import router

app = FastAPI(
    title="Gender Detection API",
    description="웹소켓을 통해 비디오 스트림에서 성별을 감지하는 API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 경로
    redoc_url="/redoc"  # ReDoc 경로
)

# API 컨트롤러
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)