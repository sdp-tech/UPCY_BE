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
from users.models import User, ReformerProfile, Certification
from users.selectors import UserSelector
# from core.exceptions import ApplicationError


JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class UserService:
    def __init__(self):
        pass

    # #리포머회원가입
    # def reformer_sign_up(
    #         email: str, 
    #         password: str, 
    #         nickname:str, 
    #         phone:str, 
    #         profile_image: InMemoryUploadedFile,
    #         thumbnail_image : InMemoryUploadedFile,
    #         agreement_terms:bool,
    #         market_name : str,
    #         market_intro : str,
    #         links : str,
    #         area : str,
    #         work_style:list[str],
    #         school_ability : str,
    #         school_certification : InMemoryUploadedFile,
    #         career_ability : str,
    #         career_certification : InMemoryUploadedFile,
    #         license_ability : str,
    #         license_certification: InMemoryUploadedFile,
    #         freelancer_ability : str,
    #         freelancer_certification: InMemoryUploadedFile,
    #         contest_ability : str,
    #         contest_certification: InMemoryUploadedFile,
    #         etc_ability : str,
    #         etc_certification: InMemoryUploadedFile,
    #         special_material : list[str],
    #         ):

    #     # ext = certificate_studentship.name.split(".")[-1]
    #     # file_path = '{}.{}'.format(str(time.time())+str(uuid.uuid4().hex), ext)
    #     # certificate_studentship = ImageFile(io.BytesIO(certificate_studentship.read()), name=file_path)

    #     user = User(
    #         is_reformer=True,
    #         email = email,
    #         nickname = nickname,
    #         password = password,
    #         phone = phone,
    #         profile_image = profile_image,
    #         thumbnail_image  = thumbnail_image,
    #         agreement_terms=agreement_terms,
    #         market_name = market_name,
    #         market_intro=market_intro,
    #         links = links,
    #         area = area,
    #         school_ability = school_ability,
    #         school_certification = school_certification,
    #         career_ability = career_ability,
    #         career_certification = career_certification,
    #         license_ability = license_ability,
    #         license_certification = license_certification,
    #         freelancer_ability = freelancer_ability,
    #         freelancer_certification = freelancer_certification,
    #         contest_ability = contest_ability,
    #         contest_certification = contest_certification,
    #         etc_ability = etc_ability,
    #         etc_certification = etc_certification,
    #     )

    #     user.set_password(password)
    #     user.is_active = True
    #     user.save()

    #     user.work_style.set(work_style)
    #     user.special_material.set(special_material)

    # #소비자회원가입
    # def consumer_sign_up(
    #         email: str,
    #         password: str,
    #         nickname: str,
    #         phone: str,
    #         profile_image: InMemoryUploadedFile,
    #         agreement_terms: bool,
    #         area: str,
    #         prefer_style:list[str],
    #         ):
        
    #     user = User(
    #         email = email,
    #         nickname = nickname,
    #         password = password,
    #         phone = phone,
    #         profile_image = profile_image,
    #         is_consumer = True,
    #         agreement_terms = agreement_terms,
    #         area = area,
    #     )

    #     user.set_password(password)
    #     user.is_active = False
    #     user.save()

    #     user.prefer_style.set(prefer_style)

    def user_sign_up(email:str,password:str,re_password:str, area:str):
        if password!=re_password:
            raise APPLICATION_ERROR(
                "비밀번호를 다시 확인해주세요."
            )
        user=User(email=email, password=password, area=area,)
        
        user.set_password(password)
        user.is_active=False
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
    
    def reformer_profile_register(self,user:User, nickname:str, market_name:str,market_intro:str,links:str,area:str,
        work_style:list[str],special_material:list[str]):
        
        reformer=ReformerProfile(user=user,nickname=nickname,market_name=market_name, market_intro=market_intro,
                                 links=links,)
        reformer.save()
        reformer.work_style.set(work_style)
        reformer.special_material.set(special_material)
    #reformer 학력 파일 등 파일 필드 서버로 추가 기능 필요(현재 로컬에 저장됨)
    
    def certification_register(self,profile:ReformerProfile,name:str,issuing_authority:str,issue_date:datetime,proof_document:InMemoryUploadedFile):
        certification=Certification(profile=profile,name=name,issuing_authority=issuing_authority,issue_date=issue_date)

        ext = proof_document.name.split(".")[-1]
        file_path = 'users/profile/certification/{}{}'.format(str(time.time())+str(uuid.uuid4().hex), ext)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        #proof_document = File(io.BytesIO(proof_document.read()), name=file_path)
        certification.proof_document.save(file_path, ContentFile(proof_document.read()), save=False)
        certification.save()
