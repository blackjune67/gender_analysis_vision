from fastapi import FastAPI, WebSocket
from app.api.websocket import websocket_endpoint
app = FastAPI()

# API 컨트롤러

app.include_router(websocket_endpoint)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)