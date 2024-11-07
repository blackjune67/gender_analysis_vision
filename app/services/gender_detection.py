from ultralytics import YOLO
from mtcnn import MTCNN
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
from logging_loki import LokiHandler
from time import time
import cv2
import numpy as np
import torch
import logging
import traceback

# 모델 초기화
yolo_model = YOLO("yolo11n.pt")
face_detector = MTCNN()
processor = AutoImageProcessor.from_pretrained("rizvandwiki/gender-classification")
gender_model = AutoModelForImageClassification.from_pretrained("rizvandwiki/gender-classification")

# 로그 설정
loki_handler = LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"application": "gender_analysis_vision"},
    version="1",
)

# 파일 핸들러 추가
file_handler = logging.FileHandler('gender_detection.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # 로깅 레벨을 DEBUG로 변경
logger.addHandler(loki_handler)
logger.addHandler(file_handler)

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

        # YOLO 처리
        try:
            results = yolo_model(frame)
            detections = results[0].boxes
        except Exception as e:
            logging.error(f"YOLO 처리 오류: {str(e)}")
            return None

        result_list = []
        
        for box in detections:
            try:
                if int(box.cls[0].item()) == 0:  # person
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    if any(coord < 0 for coord in [x1, y1, x2, y2]):
                        continue
                    
                    person_image = frame[y1:y2, x1:x2]
                    if person_image.size == 0:
                        continue

                    # MTCNN 얼굴 검출
                    faces = face_detector.detect_faces(person_image)
                    for face in faces:
                        try:
                            x, y, width, height = face['box']
                            x, y = abs(x), abs(y)
                            if x + width > person_image.shape[1] or y + height > person_image.shape[0]:
                                continue
                                
                            face_image = person_image[y:y+height, x:x+width]
                            if face_image.size == 0:
                                continue

                            # 성별 분류
                            face_image_pil = Image.fromarray(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))
                            inputs = processor(images=face_image_pil, return_tensors="pt")
                            outputs = gender_model(**inputs)
                            logits = outputs.logits
                            predicted_class_idx = logits.argmax(-1).item()

                            gender_label = '남성' if predicted_class_idx == 1 else '여성'
                            confidence = torch.softmax(logits, dim=-1).max().item()

                            result_list.append({
                                "gender": gender_label,
                                "confidence": confidence,
                                "bbox": [x1, y1, x2, y2]
                            })

                            logging.info(f"[프레임 {frame_processor.frame_count}] 인식 결과: {gender_label}, 정확도: {confidence:.2f}")
                        
                        except Exception as e:
                            logging.error(f"얼굴 처리 중 오류 발생: {str(e)}")
                            continue

            except Exception as e:
                logging.error(f"사람 검출 처리 중 오류 발생: {str(e)}")
                continue

        return result_list

    except Exception as e:
        error_traceback = traceback.format_exc()
        logging.error(f"프레임 처리 중 심각한 오류 발생:\n{error_traceback}")
        frame_processor.error_count += 1
        
        # 연속적인 에러 발생 시 로깅
        if frame_processor.error_count > 5:
            logging.critical(f"연속적인 오류 발생 감지됨: {frame_processor.error_count}회")
        
        return None