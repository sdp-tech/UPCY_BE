from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.core.exceptions import ValidationError
import re
from email.policy import default
from core.models import TimeStampedModel

#UserManager
class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(('THe Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)
    
#사용자 유형 유효성 검사
# def user_type_is_valid(self):

#     sdp_admin_user = self.is_sdp_admin and not self.is_verified
#     verified_user = not self.is_sdp_admin and self.is_verified
#     general_user = not self.is_sdp_admin and not self.is_verified

#     return sdp_admin_user | verified_user | general_user

#이메일 유효성 검사
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
    username = None
    
    #재학여부 선택 상수
    SCHOOL_ENROLLED = 'enrolled'
    SCHOOL_LEAVEOFABSENCE = 'leave_of_absence'
    SCHOOL_GRADUATED = 'graduated'
    SCHOOL_CHOICES = (
        (SCHOOL_ENROLLED, 'Enrolled'),
        (SCHOOL_LEAVEOFABSENCE, 'LeaveOfAbsence'),
        (SCHOOL_GRADUATED, 'Graduated'),
    )

    email = models.EmailField(max_length=64, unique=True)
    phone = models.CharField(max_length = 15, blank=True)
    code = models.CharField(max_length=5, blank=True)
    nickname = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to=get_upload_path, default = 'user_profile_image.png')
    agreement_terms = models.BooleanField(default = False)
    follows = models.ManyToManyField("users.User", related_name='followers', blank=True)
    is_superuser = models.BooleanField(default=False)
    # is_sdp_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default = False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default = False)

    #리폼러, 소비자 여부
    is_reformer = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=False)

    #리폼러 가입시 필요 필드
    school = models.CharField(max_length=20, blank=True)
    is_enrolled = models.CharField(choices=SCHOOL_CHOICES, max_length=20, blank=True)
    area = models.CharField(max_length=50, blank=True)
    career = models.TextField(blank=True)
    work_style = models.ManyToManyField("users.Style", related_name = 'styled_refomers', blank=True)
    bios = models.TextField(blank=True)
    certificate_studentship = models.ImageField(upload_to = get_upload_path, default= 'student_certificate_image.png')

    #소비자 가입시 필요 필드
    prefer_style = models.ManyToManyField("users.Style", related_name = 'styled_consumers', blank=True)

    # 소셜 계정인 경우, 소셜 ID 프로바이더 값 저장(ex. kakao, naver, google)
    social_provider = models.CharField(max_length=30, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def clean(self):
        if not email_isvalid(self.email):
            raise ValidationError('메일 형식이 올바르지 않습니다.')
        # if not user_type_is_valid(self):
        #     raise ValidationError('유저 타입이 잘못되었습니다.')

#Portfolio_Photo 모델 만들기
def get_portfolio_photo_upload_path(instance, filename):
    return 'users/protfolio/{}'.format(filename)

class PortfolioPhoto(TimeStampedModel):
    image = models.ImageField(
        upload_to=get_portfolio_photo_upload_path, default='portfolio_photo.png')
    user = models.ForeignKey(
        'users.User', related_name='portfolio_photos', on_delete=models.CASCADE, null=False, blank=False)

#Style 모델 만들기
class Style(models.Model):
    name = models.CharField(max_length=200)