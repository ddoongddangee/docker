FROM python:3.10-slim

WORKDIR /app

# 시스템 의존성 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 소스 복사
COPY . .

# 포트 노출 (문서화 용도)
EXPOSE 8501

# 컨테이너 실행 시 Streamlit 서버 실행 (환경변수 없이 0.0.0.0 바인딩 설정)
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
