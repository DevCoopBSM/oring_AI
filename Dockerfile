# Python 3.11.3-slim 이미지를 사용합니다.
FROM python:3.11.3-slim

# 환경변수 설정 (최적화를 위한 비표준 로컬 캐시 경로 비활성화)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# 작업 디렉토리를 설정합니다.
WORKDIR /app

# 시스템 패키지 설치 (Selenium 실행을 위한 필요 패키지 포함)
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libnss3 \
    libgconf-2-4 \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 필요한 Python 라이브러리를 설치합니다.
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 애플리케이션 소스 코드를 복사합니다.
COPY . .

# 포트 설정 (FastAPI 기본 포트)
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
