# 실시간 영상 분석

본 프로젝트는 실시간 영상 스트리밍을 분석하여 성별 구별 및 나이 추정을 수행하는 시스템입니다. FastAPI를 기반으로 구축된 백엔드와 DeepFace를 활용한 분석 모듈이 Docker 컨테이너 환경에서 동작하며, WebSocket 통신을 통해 실시간으로 데이터를 송수신합니다.

## 프로젝트 구조

### 주요 구성 요소
- **언어**: Python
- **백엔드 프레임워크**: FastAPI
- **분석 모듈**: DeepFace
- **컨테이너화**: Docker, Docker Compose

### 시스템 구성도
![System Diagram](/gender_diagram.drawio.png)

### 주요 기능
1. **실시간 영상 분석**
   - 웹소캣(WebSocket) 통신을 통해 클라이언트로부터 실시간 영상 데이터를 수신.
2. **성별 구별 및 나이 추정**
   - DeepFace 라이브러리를 활용하여 영상 데이터를 분석.
3. **결과 송신**
   - 분석 결과를 클라이언트로 실시간 반환.

---

## 설치 및 실행 방법

### 1. 사전 요구 사항
- `requiremonts.txt` 파일 참고
- **Python** (>= 3.11.6)
- **Docker** 및 **Docker Compose**
- **FastAPI**, **DeepFace**, **WebSocket 라이브러리**

### 2. 코드 다운로드
```bash
git clone https://github.com/blackjune67/gender_analysis_vision.git
cd gender_analysis_vision
```

### 3. 실행 방법
gender_analysis_vision 위치에서 아래 명령어 실행
```bash
python -m app.main
```