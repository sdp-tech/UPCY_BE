from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet


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


class ReformerManager(models.Manager):

    def create_reformer(self, **kwargs):
        return self.create(**kwargs)
