# pull official base image
FROM python:3.10-alpine as builder

# ubuntu 사용자 및 그룹 추가
RUN addgroup -S ubuntu && adduser -S ubuntu -G ubuntu

# 로그 디렉토리 및 파일 생성
RUN mkdir -p /var/log/uwsgi/UPCY
RUN chown -R ubuntu:ubuntu /var/log/uwsgi

# 의존성 패키지 설치 및 삭제
RUN apk update && apk add python3 python3-dev mariadb-dev build-base coreutils linux-headers pcre-dev gcc musl-dev python3-dev mariadb-connector-c-dev
RUN pip install ruamel.yaml.clib

# 애플리케이션 디렉토리로 작업 디렉토리 설정
WORKDIR /home/ubuntu/UPCY_BE

# 가상 환경 생성
RUN python3 -m venv /home/ubuntu/myvenv

# requirements.txt 파일을 복사한 후 패키지 설치
COPY requirements.txt /home/ubuntu/UPCY_BE/requirements.txt
RUN /home/ubuntu/myvenv/bin/pip install --upgrade pip
RUN /home/ubuntu/myvenv/bin/pip install -r requirements.txt

# 애플리케이션 소스 복사
COPY . /home/ubuntu/UPCY_BE/

# 소유자 변경
RUN chown -R ubuntu:ubuntu /home/ubuntu/UPCY_BE

USER ubuntu

# 기본 명령어 설정
ENTRYPOINT ["/home/ubuntu/myvenv/bin/uwsgi", "--ini", "/home/ubuntu/UPCY_BE/.config/uwsgi/UPCY.ini"]
