import logging
from fastapi import FastAPI, WebSocket
from app.api.websocket import router
# from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = FastAPI()

# instrumentator = Instrumentator().instrument(app)
# instrumentator.expose(app, include_in_schema=False)

# API 컨트롤러
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)