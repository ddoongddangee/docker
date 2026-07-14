# BJJ Training Recommender

본 프로젝트는 주짓수 플레이 스타일별 맞춤형 웨이트, 카디오, 드릴을 추천하는 웹 애플리케이션입니다.

## 아키텍처

- **백엔드**: FastAPI (`back/`)
- **프론트엔드**: Streamlit (`front/`)

프론트엔드는 추천 로직을 처리하지 않으며, 모든 계산은 백엔드에서 8가지 플레이 스타일에 맞추어 이루어집니다.

## Docker로 실행하는 방법

### 1. 백엔드(FastAPI) 실행
```bash
# 1) 백엔드 이미지 빌드
cd back
docker build -t bjj-backend .

# 2) 백엔드 컨테이너 실행 (8000 포트)
docker run -d --name backend_container -p 8000:8000 bjj-backend
cd ..
```
*백엔드 컨테이너가 실행되면 `http://localhost:8000/docs` 에서 API 문서를 확인할 수 있습니다.*

### 2. 프론트엔드(Streamlit) 실행
프론트엔드는 통신할 백엔드 주소가 필요합니다. Docker Network를 수동으로 연결하거나 환경변수로 주소를 지정해 실행할 수 있습니다.
여기서는 호스트 IP를 이용한 가장 기본적인 환경변수 오버라이드 방식과 Docker Network를 사용하지 않는 방법입니다. (로컬 환경 기준)

```bash
# 1) 프론트엔드 이미지 빌드
cd front
docker build -t bjj-frontend .

# 2) 프론트엔드 컨테이너 실행 (8501 포트, Windows/Mac Docker Desktop의 경우 host.docker.internal을 활용하거나 로컬 호스트 IP를 입력)
docker run -d --name frontend_container -p 8501:8501 -e BACKEND_URL=http://host.docker.internal:8000/recommend bjj-frontend
cd ..
```

*프론트엔드 컨테이너가 실행되면 브라우저에서 `http://localhost:8501` 로 접속하여 UI를 사용할 수 있습니다.*

### 3. (옵션) Docker Network를 활용해 실행하기
Docker Compose 없이 Docker 명령어로 두 컨테이너를 연결하려면 다음 과정을 거칩니다.
```bash
# 1) 네트워크 생성
docker network create bjj-network

# 2) 백엔드 실행 (네트워크 연결 및 별칭 지정)
docker run -d --name backend --network bjj-network -p 8000:8000 bjj-backend

# 3) 프론트엔드 실행 (네트워크 연결)
docker run -d --name frontend --network bjj-network -p 8501:8501 -e BACKEND_URL=http://backend:8000/recommend bjj-frontend
```

## 주요 파일 구조
- `back/main.py`: Pydantic 모델 검증, 8가지 스타일 기반 Rule Engine 추천 응답
- `front/app.py`: Streamlit UI, 백엔드 연동, 결과 카드 형태 렌더링
