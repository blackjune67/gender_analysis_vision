# 베이스 이미지 설정
FROM python:3.9-slim
# FROM amazonlinux:2

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# RUN python3 -m pip install --upgrade pip

# 작업 디렉터리 생성
WORKDIR /gender_analysis_vision

# pip 최신 버전 업그레이드
RUN pip install --upgrade pip

# 요구사항 파일을 컨테이너로 복사
COPY requirements.txt .

# 패키지 설치
# RUN python3 -m pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install -r /app/requirements.txt

# COPY yolo11n.pt . 
COPY . .

RUN mkdir -p /gender_analysis_vision/app/api /gender_analysis_vision/app/services \
    && touch /gender_analysis_vision/app/__init__.py \
    && touch /gender_analysis_vision/app/api/__init__.py \
    && touch /gender_analysis_vision/app/services/__init__.py

ENV PYTHONPATH=/gender_analysis_vision

# 실행 권한 설정
RUN chmod -R 755 /gender_analysis_vision

# 컨테이너 외부에서 접근할 수 있도록 포트 설정
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]