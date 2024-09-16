# UPCY 백엔드 환경 구성 방법
   
## 1. poetry 설치

### 우분투의 경우,
```shell
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

![image](https://github.com/user-attachments/assets/ad611fe7-06ef-4acf-9cea-547c04a3b413)
