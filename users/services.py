import os
import string
import random
import datetime

import io
import time
import uuid
from xmlrpc.client import APPLICATION_ERROR

from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
# from django.utils.encoding import force_str, force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.template.loader import render_to_string

from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_jwt.settings import api_settings
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File
from django.core.files.base import ContentFile
from users.models import User, ReformerProfile, Certification, Competition, Internship, Freelancer, UserProfile
from users.selectors import UserSelector
# from core.exceptions import ApplicationError
from core.utils import s3_file_upload_by_file_data


JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class UserService:
    def __init__(self):
        pass

    def user_sign_up(email:str,password:str,re_password:str, area:str):
        if password!=re_password:
            raise ValueError("passwords do not match")
        print("password verification passed")

        user = User.objects.create_user(email=email, password=password)
        user.save()

    def login(self, email: str, password: str):
        selector = UserSelector()

        user = selector.get_user_by_email(email)

        # if user.social_provider:
        #     raise ApplicationError(
        #         user.social_provider + " 소셜 로그인 사용자입니다. 소셜 로그인을 이용해주세요."
        #     )

        if not selector.check_password(user, password):
            raise exceptions.ValidationError(
                {'detail': "아이디나 비밀번호가 올바르지 않습니다."}
            )
        
        token = RefreshToken.for_user(user=user)

        data={
            "email": user.email,
            'refresh':str(token),
            'access': str(token.access_token),
            'nickname': user.nickname,
            'is_reformer': user.is_reformer,
            'is_consumer': user.is_consumer,
        }

        return data
    
    def user_profile_image_register(self,user:User,img:ImageFile):
        img_url=s3_file_upload_by_file_data(
            upload_file=img,
            region_name=settings.AWS_S3_REGION_NAME,
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
            bucket_path=f'profile/{user.pk}/img'
        )
        
        user_profile=UserProfile(user=user,profile_image=img_url)
        user_profile.save()
        data={
            "email":user_profile.user.email,
            "nickname":user_profile.user.nickname,
            "img":user_profile.profile_image,
        }
        return data
        
    def reformer_profile_register(self,user:User, nickname:str, market_name:str,market_intro:str,links:str,
        work_style:list[str],special_material:list[str]):
        
        reformer=ReformerProfile(user=user,nickname=nickname,market_name=market_name, market_intro=market_intro,
                                 links=links,)
        reformer.save()
        reformer.work_style.set(work_style)
        reformer.special_material.set(special_material)
    #reformer 학력 파일 등 파일 필드 서버로 추가 기능 필요(현재 로컬에 저장됨)
    
    def certification_register(self,profile:ReformerProfile,name:str,issuing_authority:str,issue_date:datetime,proof_document:InMemoryUploadedFile):
        # 파일을 S3에 업로드
        file_url = s3_file_upload_by_file_data(
            upload_file=proof_document,
            region_name=settings.AWS_S3_REGION_NAME,
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
            bucket_path=f'profile/{profile.user.pk}/certification'
        )

        # Certification 인스턴스 생성 및 저장
        certification = Certification(
            profile=profile,
            name=name,
            issuing_authority=issuing_authority,
            issue_date=issue_date,
            proof_document=file_url  # S3 파일 URL 저장
        )
        certification.save()
        
        
    def competition_register(self,profile:ReformerProfile,name:str,organizer:str,award_date:str,proof_document:InMemoryUploadedFile):
        # 파일을 S3에 업로드
        file_url = s3_file_upload_by_file_data(
            upload_file=proof_document,
            region_name=settings.AWS_S3_REGION_NAME,
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
            bucket_path=f'profile/{profile.user.pk}/competition'
        )
        competition=Competition(
            profile=profile,
            name=name,
            organizer=organizer,
            award_date=award_date,
            proof_document=file_url,
        )
        competition.save()
        
    def intership_register(self,profile:ReformerProfile,company_name:str,department:str,position:str,start_date:str,end_date:str,proof_document:InMemoryUploadedFile):
        # 파일을 S3에 업로드
        file_url = s3_file_upload_by_file_data(
            upload_file=proof_document,
            region_name=settings.AWS_S3_REGION_NAME,
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
            bucket_path=f'profile/{profile.user.pk}/intership'
        )        
        
        internship=Internship(
            profile=profile,company_name=company_name,department=department,position=position,start_date=start_date,end_date=end_date,
                    proof_document=file_url,
        )
        internship.save()
        
    def freelancer_register(self,profile:ReformerProfile,project_name:str,client:str,main_tasks:str,start_date:str,end_date:str,proof_document:InMemoryUploadedFile):
        # 파일을 S3에 업로드
        file_url = s3_file_upload_by_file_data(
            upload_file=proof_document,
            region_name=settings.AWS_S3_REGION_NAME,
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
            bucket_path=f'profile/{profile.user.pk}/freelancer'
        )        
        freelancer=Freelancer(
            profile=profile,project_name=project_name,client=client,main_tasks=main_tasks,start_date=start_date,end_date=end_date,
                    proof_document=file_url)
        freelancer.save()   