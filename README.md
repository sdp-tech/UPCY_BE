# 프로젝트 아키텍쳐

다시 그릴 예정..

# 사용 기술
- Django
- Gunicorn
- DRF
- Docker
- PostgreSQL

# UPCY 백엔드 환경 구성 방법
   
## 1. poetry 설치

### 우분투의 경우,
```shell
git clone -b upcy-14th-backend-dev https://github.com/sdp-tech/UPCY_BE.git
sudo apt update
sudo apt install poetry
```

## 2. 의존성 설치
```shell
poetry config virtualenvs.in-project true
poetry install --no-root
```

> 따로 가상환경 폴더를 설정하지 않은 경우, ubuntu 기준 다음과 같은 경로에 설치됩니다. 해당 경로를 인터프리터 경로로 잡아주시면 됩니다.
> - Virtualenv location: /home/USERNAME/.local/share/virtualenvs/UPCY_BE-rtTVnQO9

## 3. 가상환경 실행
```shell
poetry shell
```

## 4. Database migration
```shell
python manage.py migrate
```

## 5. 서버 실행
```shell
python manage.py runserver
```

## Production (Test)
```shell
sudo docker run -d --name upcy-be-container -p 8000:8000 sullungim/upcy-be:latest # EC2에서 실행
sudo docker container ls # 실행중인 컨테이너 리스트 확인
sudo docker logs -f {container_id} # 콘솔 로그 보는 방법
```