import logging
from fastapi import FastAPI, WebSocket
from app.api.websocket import router
# from prometheus_fastapi_instrumentator import Instrumentator

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 콘솔에 로그 출력
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)

# 파일에 로그 저장 (localLog.log)
file_handler = logging.FileHandler("/Users/highbuff/Repository/gender_analysis_vision/logs/localLog.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = FastAPI()

# instrumentator = Instrumentator().instrument(app)
# instrumentator.expose(app, include_in_schema=False)

# API 컨트롤러
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)