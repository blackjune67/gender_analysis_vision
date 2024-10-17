from ultralytics import YOLO
from mtcnn import MTCNN
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import cv2
import numpy as np
import torch

# 모델 초기화
yolo_model = YOLO("yolo11n.pt")
face_detector = MTCNN()
processor = AutoImageProcessor.from_pretrained("rizvandwiki/gender-classification")
gender_model = AutoModelForImageClassification.from_pretrained("rizvandwiki/gender-classification")

def process_frame(data):
    nparr = np.frombuffer(data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # YOLO로 사람 탐지
    results = yolo_model(frame)
    detections = results[0].boxes
    
    result_list = []
    
    for box in detections:
        if int(box.cls[0].item()) == 0:  # 'person'인 경우만 처리
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            person_image = frame[y1:y2, x1:x2]
            
            # MTCNN을 사용해 얼굴 검출
            faces = face_detector.detect_faces(person_image)
            for face in faces:
                x, y, width, height = face['box']
                x, y = abs(x), abs(y)
                face_image = person_image[y:y+height, x:x+width]

                # 성별 분류
                face_image_pil = Image.fromarray(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))
                inputs = processor(images=face_image_pil, return_tensors="pt")
                outputs = gender_model(**inputs)
                logits = outputs.logits
                predicted_class_idx = logits.argmax(-1).item()

                # 성별 예측
                gender_label = '남성' if predicted_class_idx == 1 else '여성'
                confidence = torch.softmax(logits, dim=-1).max().item()

                # 결과 저장
                result_list.append({
                    "gender": gender_label,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2]
                })
    return result_list
