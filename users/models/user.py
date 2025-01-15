import faker
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet

random_generator = faker.Faker("ko_KR")


def get_user_profile_image_upload_path(instance, filename):
    email_name = instance.email.split("@")[0]
    return f"users/{email_name}/profile-image/{filename}"


def default_nickname_generator(email):
    email_name, domain = email.split(".")[0].split("@")

    return (email_name + domain + str(random_generator.random_number(digits=20)))[:30]


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)

        try:
            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            user.save()
        except ValidationError as e:
            print(f"Validation Error: {str(e)}")
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            print(f"An error occurred during sign-up: {str(e)}")
            raise Exception(f"An error occurred during sign-up: {str(e)}")
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

    def get_user_by_email(self, email: str) -> QuerySet:
        # 이메일을 사용하여 사용자 정보 쿼리셋을 생성하는 함수
        return self.model.objects.filter(email=email)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=64, unique=True)  # 이메일
    phone = models.CharField(max_length=15, null=True, blank=True)  # 휴대전화 번호
    full_name = models.CharField(max_length=40, null=True, blank=True)  # 실명
    nickname = models.CharField(max_length=40, unique=True, blank=True)  # 사용자 닉네임
    agreement_terms = models.BooleanField(
        default=False
    )  # 선택 약관 동의 여부 -> 필수 약관은 프론트에서 알아서 처리한다고 합니다
    address = models.CharField(
        max_length=255, null=True, blank=True
    )  # 사용자 기본 주소
    profile_image = models.FileField(
        upload_to=get_user_profile_image_upload_path, null=True, blank=True
    )  # 프로필 이미지 필드
    introduce = models.TextField(null=True, blank=True)  # 사용자 소개글
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    role = models.CharField(
        choices=[
            ("customer", "CUSTOMER"),
            ("reformer", "REFORMER"),
            ("admin", "ADMIN"),
        ],
        max_length=20,
        null=False,
        default="customer",
    )  # 사용자 타입 (일반 사용자, 리포머, 관리자)
    # customer 가입시 사용하는 필드

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.nickname:  # 회원가입 시 nickname을 전달받지 못했다면, 랜덤으로 생성
            nickname = default_nickname_generator(self.email)
            self.nickname = nickname
        super().save(*args, **kwargs)

    class Meta:
        db_table = "users"


class UserPreferStyle(models.Model):
    # 사용자의 선호 스타일 저장 테이블
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    prefer_style = models.CharField(max_length=100)

    class Meta:
        db_table = "user_prefer_style"
