from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.services.gender_detection import process_frame, FrameProcessor
from typing import Dict
from app.models.response_models import GenderDetectionResponse, GenderResult
import asyncio
import logging
import traceback

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.frame_processors: Dict[str, FrameProcessor] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        client_id = id(websocket)
        self.active_connections[client_id] = websocket
        self.frame_processors[client_id] = FrameProcessor(frame_interval=5)
        logging.info(f"새 클라이언트 연결 ID: {client_id}")
        return client_id

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.frame_processors:
            del self.frame_processors[client_id]
        logging.info(f"끊긴 클라이언트 ID: {client_id}")

    async def send_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logging.error(f"에러 메시지: {str(e)}")
            raise

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    ### 웹소켓 엔드포인트
    - **설명**: 웹 소캣을 통해 클라이언트와 연결하고, 프레임을 처리하여 결과를 반환합니다.
    - **경로**: `/ws`
    - **클라이언트 연결**: `websocket.connect("/ws")`
    """
    client_id = None
    try:
        client_id = await manager.connect(websocket)
        logging.info(f"클라이언트에 대한 웹소켓 연결 설정 ID: {client_id}")

        while True:
            try:
                # 클라이언트로부터 데이터 수신 대기 (타임아웃 설정)
                data = await asyncio.wait_for(
                    websocket.receive_bytes(),
                    timeout=30.0  # 30초 타임아웃
                )
                
                # 프레임 처리
                frame_processor = manager.frame_processors.get(client_id)
                result_list = process_frame(data, frame_processor)
                
                if result_list is not None:
                    response = GenderDetectionResponse(results=result_list)
                    await manager.send_message(response.model_dump(), websocket)
                
            except asyncio.TimeoutError:
                # 클라이언트 연결 상태 확인을 위한 ping 전송
                try:
                    await websocket.send_json({"ping": "keepalive"})
                    logging.debug(f"Sent keepalive ping to client {client_id}")
                except Exception as e:
                    logging.error(f"Failed to send keepalive ping: {str(e)}")
                    raise WebSocketDisconnect()

    except WebSocketDisconnect:
        logging.warning(f"WebSocket disconnected normally for client {client_id}")
        if client_id:
            manager.disconnect(client_id)

    except Exception as e:
        error_traceback = traceback.format_exc()
        logging.error(f"Unexpected error for client {client_id}:\n{error_traceback}")
        if client_id:
            manager.disconnect(client_id)
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except:
            pass

    finally:
        if client_id and client_id in manager.active_connections:
            manager.disconnect(client_id)


# @router.get("/gender-detection", response_model=GenderDetectionResponse)
# async def get_gender_detection_results():
#     """
    
#     """
#     # 테스트 응답 데이터
#     mock_result = [
#         {
#             "gender": "남성",
#             "confidence": 0.95,
#         }
#     ]
#     return {"results": mock_result}

@router.get(
        "/ws-docs", 
        tags=["웹 소캣 API"],
        response_model=GenderDetectionResponse,
        response_description="WebSocket API 사용 설명서"
)
async def get_websocket_documentation():
    """
    # WebSocket API 사용 설명서
    
    ### WebSocket 엔드포인트
    - `/ws`
    
    ### 연결 방법 예시
    - ```markdown
        const ws = new WebSocket('ws://43.201.158.217:8000/ws');
        ```
    
    ### 요청 형식
    - Binary 이미지 데이터 (JPEG/PNG)
    - 웹에서는 캡처된 이미지를 Blob으로 변환하여 전송
    
    ### 응답 형식
    - ```markdown
        {
            "results": [
                {
                "gender": "남성",
                "confidence": 0.95
                }
            ]
        }
        ```

    ### 주의사항
    - 30초 타임아웃 설정
    - 5프레임마다 처리
    - 연결이 끊어질 경우 재연결 로직 필요
    """
    # return {
    #     "results": [
    #             {
    #                 "gender": "남성",
    #                 "confidence": 0.95
    #             }
    #         ]
    # }
    return GenderDetectionResponse(
        results=[
            GenderResult(
                gender="남성",
                confidence=0.95
            )
        ]
    )