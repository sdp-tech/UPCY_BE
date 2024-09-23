# Python 3.12 slim 이미지를 기반으로 사용
FROM python:3.12-slim

# 이미지의 유지 관리자를 지정
LABEL maintainer="sullungim"

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    TZ=Asia/Seoul \
    POETRY_HOME=/opt/poetry \
    PATH="/opt/poetry/bin:$PATH" \
    POETRY_VIRTUALENVS_CREATE=false

# 필요한 패키지 설치 및 Poetry 설치
RUN apt-get update && \
    apt-get install --no-install-recommends -y curl tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    poetry --version

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 파일 복사
COPY pyproject.toml poetry.lock ./

# 프로젝트 의존성 설치
RUN poetry install --no-root --no-interaction

# 프로젝트 파일 복사
COPY . .

# 시간대 설정
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 사용자 추가 및 권한 설정
RUN adduser --disabled-password --no-create-home --uid 1000 django-user && \
    chown -R django-user:django-user /app

# 로그 디렉토리 설정
RUN mkdir -p /app/logs && \
    chown -R django-user:django-user /app/logs

# 포트 노출
EXPOSE 8000

# 사용자 전환
USER django-user

# Django 프로젝트 실행
# Dockerfile을 사용하는 경우 = Production level
# 개발시에는 그냥 터미널 열고 python manage.py runserver로 실행해주세용
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && gunicorn --workers 3 --bind 0.0.0.0:8000 config.wsgi:application"]
# CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]