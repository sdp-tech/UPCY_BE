import datetime
from typing import Dict

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import exceptions
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.utils import s3_file_upload_by_file_data
from users.models import (ReformerAwards, ReformerCareer, ReformerCertification, Freelancer,
                          ReformerProfile, User, UserProfile)
from users.selectors import UserSelector

# JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
# JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class UserService:
    def __init__(self):
        pass

    @staticmethod
    def user_sign_up(email: str, password: str, agreement_terms: bool, address: str) -> None:
        """
        사용자 회원가입 함수
        """
        try:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                raise ValidationError('A user with this email already exists.')


            # Create user with provided details
            user = User.objects.create_user(
                email=email,
                password=password,
                agreement_terms=agreement_terms,
                address=address
            )
            user.save()
        except ValidationError as e:
            # Handle specific validation errors
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            # Handle unexpected errors
            raise Exception(f"An error occurred during sign-up: {str(e)}")

    @staticmethod
    def login(email: str, password: str) -> Dict:
        """
        사용자 로그인 함수 -> 로그인 성공 시 AccessToken, RefreshToken 발급
        """
        selector = UserSelector()
        user = selector.get_user_by_email(email)

        if not selector.check_password(user, password):
            raise exceptions.ValidationError("아이디나 비밀번호가 올바르지 않습니다.")
        
        token = RefreshToken.for_user(user=user)

        data={
            "access": str(token.access_token),
            "refresh": str(token)
        }

        return data

    @staticmethod
    def logout(refresh_token: str) -> None:
        try:
            # refresh token 유효성 검사 및 블랙리스트 처리
            token = RefreshToken(refresh_token)
            token.blacklist()  # 블랙리스트에 추가하여 사용 불가 처리
        except (TokenError, InvalidToken) as e:
            raise e
        except Exception as e:
            raise e

    def user_profile_image_register(self, user: User, img: ImageFile) -> Dict:
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
        
    def reformer_profile_register(self, user: User, nickname: str, market_name: str,market_intro: str, links: str,
        work_style: list[str], special_material: list[str]):
        
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
        certification = ReformerCertification(
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
        award=ReformerAwards(
            profile=profile,
            name=name,
            organizer=organizer,
            award_date=award_date,
            proof_document=file_url,
        )
        award.save()
        
    def intership_register(self,profile:ReformerProfile,company_name:str,department:str,position:str,start_date:str,end_date:str,proof_document:InMemoryUploadedFile):
        # 파일을 S3에 업로드
        file_url = s3_file_upload_by_file_data(
            upload_file=proof_document,
            region_name=settings.AWS_S3_REGION_NAME,
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
            bucket_path=f'profile/{profile.user.pk}/intership'
        )        
        
        career = ReformerCareer(
            profile=profile,company_name=company_name,department=department,position=position,start_date=start_date,end_date=end_date,
                    proof_document=file_url,
        )
        career.save()
        
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