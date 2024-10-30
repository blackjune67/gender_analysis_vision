# import logging
from fastapi import FastAPI, WebSocket
from api.websocket import router

app = FastAPI()

# API 컨트롤러
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)