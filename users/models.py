import re

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.exceptions import ValidationError
from django.db import models

from core.models import TimeStampedModel

#Portfolio photo 모델
def get_portfolio_photo_upload_path(instance, filename):
    return 'users/portfolio/{}'.format(filename)

def get_reformer_certification_upload_path(instance, filename):
    user_id = instance.reformer.user.id
    return f"users/{user_id}/certifications/{filename}"

def get_user_profile_image_upload_path(instance, filename):
    user_id = instance.id
    return f"users/{user_id}/profile/{filename}"

def email_isvalid(value):
    try:
        validation = re.compile(
            r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if not re.match(validation, value):
            raise Exception('올바른 메일 형식이 아닙니다.')
        return value
    except Exception as e:
        print('예외가 발생했습니다.', e)


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


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=64, unique=True)  # 이메일
    phone = models.CharField(max_length=15, null=True, blank=True)  # 휴대전화 번호
    nickname = models.CharField(max_length=20, null=True, blank=True)  # 사용자 닉네임
    agreement_terms = models.BooleanField(default=False)  # 약관 동의 여부
    address = models.CharField(max_length=255, null=True, blank=True)  # 사용자 기본 주소
    profile_image = models.FileField(upload_to=get_user_profile_image_upload_path, null=True, blank=True) # 프로필 이미지 필드
    introduce = models.TextField(null=True, blank=True) # 사용자 소개글
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    role = models.CharField(
        choices=[("customer", "CUSTOMER"), ("reformer", "REFORMER"), ("admin", "ADMIN")],
        max_length=20,
        null=False,
        default="customer"
    )  # 사용자 타입 (일반 사용자, 리포머, 관리자)
    # customer 가입시 사용하는 필드

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        if not email_isvalid(self.email):
            raise ValidationError('메일 형식이 올바르지 않습니다.')


class UserPreferStyle(models.Model):
    # 사용자의 선호 스타일 저장 테이블
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prefer_style = models.CharField(max_length=100)


class ReformerProfile(models.Model):
    # 리포머 기본 프로필 정보
    # 닉네임, 소개글은 User 테이블에 있는 필드 사용 -> 리포머 생성 요청 시 필요
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reformer_profile')
    reformer_link = models.TextField(blank=True, null=True) # 리포머 웹페이지 링크 (아마 오픈카톡 링크..?)
    reformer_area = models.CharField(max_length=100, null=True) # 리포머 활동 지역


class ReformerEducation(models.Model):
    # 리포머 학력
    reformer = models.ForeignKey(ReformerProfile, on_delete=models.CASCADE, related_name='education')
    school = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    academic_status = models.CharField(max_length=100)
    proof_document = models.FileField(upload_to=get_reformer_certification_upload_path, null=True, blank=True)  # S3에 저장되는 경로


class PortfolioPhoto(TimeStampedModel):
    image = models.ImageField(
        upload_to=get_portfolio_photo_upload_path, default='portfolio_photo.png')
    user = models.ForeignKey(
        'users.User', related_name='portfolio_photos', on_delete=models.CASCADE, null=False, blank=False)
    introduction = models.TextField(null=True, blank=True)


class ReformerStyle(models.Model):
    # 리포머 작업 스타일
    reformer = models.ForeignKey(ReformerProfile, on_delete=models.CASCADE, related_name='style')
    name = models.CharField(max_length=200)  # 스타일 태그 명


class ReformerMaterial(models.Model):
    # 리포머 주요 사용 재료
    reformer = models.ForeignKey(ReformerProfile, on_delete=models.CASCADE, related_name='material')
    name = models.CharField(max_length=200)  # 특수소재 명


class ReformerCertification(models.Model):
    # 리포머 자격 사항
    reformer = models.ForeignKey(ReformerProfile, on_delete=models.CASCADE, related_name='certification')
    name = models.CharField(max_length=100)
    issuing_authority = models.CharField(max_length=100)
    issue_date = models.DateField()
    proof_document = models.FileField(upload_to=get_reformer_certification_upload_path, null=True, blank=True)


class ReformerAwards(models.Model):
    # 리포머 수상 내역
    reformer = models.ForeignKey(ReformerProfile,on_delete=models.CASCADE, related_name='awards')
    name = models.CharField(max_length=100)
    organizer = models.CharField(max_length=100)
    award_date = models.DateField()
    proof_document = models.FileField(upload_to=get_reformer_certification_upload_path, null=True, blank=True)


class ReformerCareer(models.Model):
    # 리포머 경력
    reformer = models.ForeignKey(ReformerProfile, on_delete=models.CASCADE, related_name='career')
    company_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100,null=True,blank=True)
    position = models.CharField(max_length=100,null=True,blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    proof_document = models.FileField(upload_to=get_reformer_certification_upload_path, null=True, blank=True)


class ReformerFreelancer(models.Model):
    # 리포머 프리랜서/외주 경력
    reformer = models.ForeignKey(ReformerProfile, on_delete=models.CASCADE, related_name='freelancer')
    project_name = models.CharField(max_length=100)
    client = models.CharField(max_length=100)
    main_tasks = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    proof_document = models.FileField(upload_to=get_reformer_certification_upload_path, null=True, blank=True)
