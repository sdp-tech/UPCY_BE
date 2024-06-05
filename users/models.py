from django.db import models

# Create your models here.
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver
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
    email = models.EmailField(max_length=64, unique=True)
    phone = models.CharField(max_length = 15, blank=True, null=True)
    code = models.CharField(max_length=5, blank=True, null=True)
    nickname = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    agreement_terms = models.BooleanField(default = False)
    follows = models.ManyToManyField("users.User", related_name='followers', blank=True)
    is_superuser = models.BooleanField(default=False)
    # is_sdp_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default = False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default = False)
    area = models.CharField(max_length=20,blank=True)
    #리폼러, 소비자 여부
    is_reformer = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=False)

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

#Reformer profile 모델
class ReformerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reformer_profile')
    # 여기에 리폼러 기본 필드
    nickname=models.CharField(max_length=50)
    work_style = models.ManyToManyField("users.Style", related_name = 'styled_refomers', blank=True)
    links = models.TextField(blank=True, null=True)
    market_name = models.CharField(max_length=50, blank=True, null=True)
    market_intro = models.TextField(blank=True, null=True)
    thumbnail_image = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    special_material = models.ManyToManyField("users.Material", related_name = 'reformers', blank=True)

    #리포머 학력
    school = models.CharField(max_length=100,blank=True,null=True)
    major = models.CharField(max_length=100,blank=True,null=True)
    status = models.CharField(max_length=100,blank=True,null=True)
    school_certification = models.FileField(null=True)

    def __str__(self):
        return self.user.email  # 또는 user의 다른 식별가능한 정보

#Portfolio photo 모델
def get_portfolio_photo_upload_path(instance, filename):
    return 'users/protfolio/{}'.format(filename)

class PortfolioPhoto(TimeStampedModel):
    image = models.ImageField(
        upload_to=get_portfolio_photo_upload_path, default='portfolio_photo.png')
    user = models.ForeignKey(
        'users.User', related_name='portfolio_photos', on_delete=models.CASCADE, null=False, blank=False)
    introduction = models.TextField(null=True, blank=True)

#Style 모델 만들기
class Style(models.Model):
    name = models.CharField(max_length=200)

#특수소재 모델
class Material(models.Model):
    name = models.CharField(max_length=200)
    
class Certification(models.Model):
    profile = models.ForeignKey(ReformerProfile,on_delete=models.CASCADE, related_name='certification')
    name = models.CharField(max_length=100)
    issuing_authority = models.CharField(max_length=100)
    issue_date = models.DateField()
    proof_document = models.FileField()

class Competition(models.Model):
    profile = models.ForeignKey(ReformerProfile,on_delete=models.CASCADE, related_name='competition')
    name = models.CharField(max_length=100)
    organizer = models.CharField(max_length=100)
    award_date = models.DateField()
    proof_document = models.FileField()
        
class Internship(models.Model):
    profile = models.ForeignKey(ReformerProfile,on_delete=models.CASCADE, related_name='internship')
    company_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100,null=True,blank=True)
    position = models.CharField(max_length=100,null=True,blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    period=models.DurationField()
    proof_document = models.FileField()
    
@receiver(pre_save, sender=Internship)
def calculate_period(sender, instance, **kwargs):
    instance.period = instance.end_date - instance.start_date if instance.start_date and instance.end_date else None

    

class Freelancer(models.Model):
    profile = models.ForeignKey(ReformerProfile,on_delete=models.CASCADE, related_name='freelancer')
    project_name = models.CharField(max_length=100)
    client = models.CharField(max_length=100)
    main_tasks = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    period=models.DurationField()
    proof_document = models.FileField()
    
@receiver(pre_save, sender=Freelancer)
def calculate_period(sender, instance, **kwargs):
    instance.period = instance.end_date - instance.start_date if instance.start_date and instance.end_date else None

    
class Outsourcing(models.Model):
    profile = models.ForeignKey(ReformerProfile,on_delete=models.CASCADE, related_name='outsourcing')
    project_name = models.CharField(max_length=100)
    client = models.CharField(max_length=100)
    main_tasks = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    period=models.DurationField()
    proof_document = models.FileField()
    
@receiver(pre_save, sender=Outsourcing)
def calculate_period(sender, instance, **kwargs):
    instance.period = instance.end_date - instance.start_date if instance.start_date and instance.end_date else None