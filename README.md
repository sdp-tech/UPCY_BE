# 프로젝트 아키텍쳐

# 사용 기술
- Django
- Gunicorn
- DRF
- Docker
- PostgreSQL
- AWS

# UPCY 백엔드 환경 구성 방법

## 0. pipx 설치 

[참고 문서](https://pipx.pypa.io/stable/installation/)
### Ubuntu
```shell
sudo apt update
sudo apt install pipx
pipx ensurepath

vim ~/.bashrc
```

- bashrc 최하단에 사진과 같이 기입 후 저장

![image](https://github.com/user-attachments/assets/d9e08953-87ba-4876-9036-5a375b1cd994)

```text
export PATH="$HOME/.local/bin:$PATH"
```

- bashrc 변경사항 적용
```shell
source ~/.bashrc
```

### MacOS
```shell
brew install pipx
pipx ensurepath
sudo pipx ensurepath --global
```

## 1. poetry 설치
[참고문서](https://python-poetry.org/docs/#installation)
### Ubuntu
```shell
pipx install poetry
```

## 2. 프로젝트 클론 및 의존성 설치
```shell
git clone -b upcy-14th-backend-dev https://github.com/sdp-tech/UPCY_BE.git
cd path/to/project
poetry config virtualenvs.in-project true
poetry install --no-root
```

> 따로 가상환경 폴더를 설정하지 않은 경우, ubuntu 기준 다음과 같은 경로에 설치됩니다. 해당 경로를 인터프리터 경로로 잡아주시면 됩니다.
> - Virtualenv location: /home/USERNAME/.local/share/virtualenvs/UPCY_BE-rtTVnQO9

> 백엔드 팀원에게 .env 파일을 제공해달라고 요청해주세요. 해당 .env 파일을 프로젝트 루트 디렉토리에 넣어주시면 됩니다.

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

# 개발 후 PR 방법

## 1. 본인 로컬 콘솔에서 아래 과정을 수행합니다.
```shell
git status # 변경상태 확인
git add . 또는 git add <파일명> # git stage (파일 추가)
git commit -m "commit message" # commit

# 원격 레포지토리에 본인이 개발한 코드를 반영하기 이전, 원격 저장소에서 발생한 변경 내역을 반영합니다.
git pull origin upcy-14th-backend-dev
# 만약 위 명령 실행 후 충돌이 발생했다면, 충돌 해결 또는 다른 백엔드 팀원에게 물어봅시다.
# 충돌 해결 후 git add, git commit을 수행합니다.

git push origin <본인이개발한브랜치이름> # 원격 레포지토리로 push
```

## 2. 깃허브에 접속하여, Pull request를 생성합니다.
```shell

```

## 3. Actions 탭을 누르거나, PR 페이지에서 Django API Test 표시 확인
```shell

```

## 4. 배포
PR 및 코드리뷰가 성공적으로 완료되어 메인 개발 브랜치로 Merge되면 본인 코드가 자동으로 배포 환경에 반영됩니다.
