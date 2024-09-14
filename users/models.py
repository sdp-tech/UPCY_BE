from django.db import models

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver
import re
from core.models import TimeStampedModel


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
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


def email_isvalid(value):
    try:
        validation = re.compile(
            r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if not re.match(validation, value):
            raise Exception('올바른 메일 형식이 아닙니다.')
        return value
    except Exception as e:
        print('예외가 발생했습니다.', e)


#ProfileImage파일 업로드 경로 설정
def get_upload_path(instance, filename):
    return 'users/profile/{}'.format(filename)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=64, unique=True)  # 이메일
    phone = models.CharField(max_length=15, null=True, blank=True)  # 휴대전화 번호, now allows blank
    nickname = models.CharField(max_length=20, null=True, blank=True)  # 사용자 닉네임, now allows blank
    agreement_terms = models.BooleanField(default=False)  # 약관 동의 여부
    address = models.CharField(max_length=255, null=True, blank=True)  # 사용자 기본 주소, ensure blank if optional
    follows = models.ManyToManyField("users.User", related_name='followers', blank=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    role = models.CharField(
        choices=[("customer", "CUSTOMER"), ("reformer", "REFORMER"), ("admin", "ADMIN")],
        max_length=20,
        null=False,
        default="customer"
    )  # 사용자 타입 (일반 사용자, 리포머, 관리자)
    # customer 가입시 사용하는 필드
    prefer_style = models.ManyToManyField("users.Style", related_name='styled_consumers', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        if not email_isvalid(self.email):
            raise ValidationError('메일 형식이 올바르지 않습니다.')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.URLField(null=True)
    introduce=models.TextField(null=True)

#Reformer profile 모델
class ReformerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reformer_profile')
    # 여기에 리폼러 기본 필드
    nickname=models.CharField(max_length=50)
    work_style = models.ManyToManyField("users.Style", related_name = 'styled_refomers', blank=True)
    links = models.TextField(blank=True, null=True)
    market_name = models.CharField(max_length=50, blank=True, null=True)
    market_intro = models.TextField(blank=True, null=True)
    special_material = models.ManyToManyField("users.Material", related_name = 'reformers', blank=True)

class ReformerEducation(models.Model):
    profile = models.ForeignKey(ReformerProfile, on_delete=models.CASCADE, related_name='education')
    school = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    academic_status = models.CharField(max_length=100)
    proof_document = models.URLField(null=True)

#Portfolio photo 모델
def get_portfolio_photo_upload_path(instance, filename):
    return 'users/protfolio/{}'.format(filename)

class PortfolioPhoto(TimeStampedModel):
    image = models.ImageField(
        upload_to=get_portfolio_photo_upload_path, default='portfolio_photo.png')
    user = models.ForeignKey(
        'users.User', related_name='portfolio_photos', on_delete=models.CASCADE, null=False, blank=False)
    introduction = models.TextField(null=True, blank=True)

# Style 모델 만들기
class Style(models.Model):
    name = models.CharField(max_length=200) # 스타일 태그 명

# 특수소재 모델
class Material(models.Model):
    name = models.CharField(max_length=200) # 특수소재 명

class Certification(models.Model):
    profile = models.ForeignKey(ReformerProfile, on_delete=models.CASCADE, related_name='certification')
    name = models.CharField(max_length=100)
    issuing_authority = models.CharField(max_length=100)
    issue_date = models.DateField()
    proof_document = models.URLField(null=True)

class Awards(models.Model):
    profile = models.ForeignKey(ReformerProfile,on_delete=models.CASCADE, related_name='awards')
    name = models.CharField(max_length=100)
    organizer = models.CharField(max_length=100)
    award_date = models.DateField()
    proof_document = models.URLField(null=True)

class Career(models.Model):
    profile = models.ForeignKey(ReformerProfile,on_delete=models.CASCADE, related_name='career')
    company_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100,null=True,blank=True)
    position = models.CharField(max_length=100,null=True,blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    proof_document = models.URLField(null=True)

class Freelancer(models.Model):
    profile = models.ForeignKey(ReformerProfile,on_delete=models.CASCADE, related_name='freelancer')
    project_name = models.CharField(max_length=100)
    client = models.CharField(max_length=100)
    main_tasks = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    proof_document = models.URLField(null=True)
