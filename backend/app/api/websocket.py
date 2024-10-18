from fastapi import APIRouter, WebSocket
from app.services.gender_detection import process_frame

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # 클라이언트로부터 영상 데이터를 WebSocket으로 받음
            data = await websocket.receive_bytes()
            result_list = process_frame(data)
            
            # 분석 결과를 클라이언트에 전송
            await websocket.send_json({"results": result_list})

    except Exception as e:
        print(f"Connection closed: {e}")
        await websocket.close()