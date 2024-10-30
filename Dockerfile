# 베이스 이미지 설정
FROM python:3.9-slim

# 작업 디렉터리 생성
WORKDIR /app

# YOLO 모델 파일과 애플리케이션 코드를 복사 (자주변경 되는 부분을 상단에 배치)
COPY yolo11n.pt . 
COPY backend/app /app

# 요구사항 파일을 컨테이너로 복사
COPY backend/requirements.txt .

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 컨테이너 외부에서 접근할 수 있도록 포트 설정
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]