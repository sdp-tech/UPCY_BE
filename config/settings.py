import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")  # 환경변수 파일 로드

SECRET_KEY = os.getenv("UPCY_SECRET_KEY")

DEBUG = os.getenv("DJANGO_DEBUG_MODE", "False").lower() in ("true", "1")
ALLOWED_HOSTS = ["*"]

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

PROJECT_APPS = [
    "users.apps.UsersConfig",
    "core.apps.CoreConfig",
    "market.apps.MarketConfig",
    "order.apps.OrderConfig",
]

LIBS = [
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "storages",
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + LIBS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "config.middleware.request_logging_middleware.RequestLoggingMiddleware",
]

# CORS / CSRF 설정
CORS_ORIGIN_ALLOW_ALL = True
CSRF_COOKIE_SECURE = False  # 개발 중일 때는 False로 설정
CSRF_TRUSTED_ORIGINS = [
    "https://3d49-165-132-5-152.ngrok-free.app",
    "https://upcy.co.kr",
]

# 기본 인증 모델
AUTH_USER_MODEL = "users.User"

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"

# REST API 사용 시 인증 관련 설정
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",  # 깔끔하게 JSON만 전달 (DRF 웹페이지 안씀)
    ),
}

REST_USE_JWT = True

# Json web token 설정
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,  # 로그아웃, Token rotate 시 블랙리스트 처리
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv("UPCY_SECRET_KEY"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",  # payload에 user id가 들어있으므로, 사용자 정보는 token에서 획득 가능함
    "USER_ID_CLAIM": "user_id",
}

# 최상위 urls.py 위치 지정
ROOT_URLCONF = "config.urls"

# API 호출 시 맨 뒤에 붙는 슬래시 기능 사용X
APPEND_SLASH = False

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database 설정
if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB_NAME"),
            "USER": os.getenv("POSTGRES_DB_USER"),
            "PASSWORD": os.getenv("POSTGRES_DB_PASSWORD"),
            "HOST": os.getenv("POSTGRES_DB_HOST"),
            "PORT": os.getenv("POSTGRES_DB_PORT"),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# 언어 및 시간 환경 설정
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# 정적파일 저장 위치
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# S3 설정
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
AWS_S3_SIGNATURE_VERSION = os.getenv("AWS_S3_SIGNATURE_VERSION")
AWS_DEFAULT_ACL = os.getenv("AWS_S3_DEFAULT_ACL")

# 업로드 파일 저장 위치 설정
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "region_name": AWS_S3_REGION_NAME,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "region_name": AWS_S3_REGION_NAME,
        },
    },
}
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 최대 파일 업로드 크기 10MB 제한

# 로깅 설정
if not DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "boto3": {
                "handlers": ["console"],
                "level": "INFO",
            },
            "botocore": {
                "handlers": ["console"],
                "level": "INFO",
            },
            "django_storages": {
                "handlers": ["console"],
                "level": "INFO",
            },
            "django.request": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "django.db.backends": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "django": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": True,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    }
