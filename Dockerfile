# pull official base image
FROM python:3.10-alpine as builder
# Dockerfile

# 기존 명령들 위에 아래 명령을 추가합니다
RUN mkdir -p /UPCY_BE/logs
RUN touch /UPCY_BE/logs/debug.log
RUN chown -R www-data:www-data /UPCY_BE/logs


# 의존성 패키지 설치 및 삭제
RUN apk update && apk add python3 python3-dev mariadb-dev build-base coreutils && pip3 install mysqlclient && apk del python3-dev mariadb-dev build-base
RUN apk add --no-cache gcc musl-dev python3-dev mariadb-connector-c-dev
RUN pip install ruamel.yaml.clib
RUN mkdir /srv/UPCY_BE
WORKDIR /srv/UPCY_BE
COPY requirements.txt /srv/UPCY_BE/requirements.txt
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /srv/UPCY_BE/