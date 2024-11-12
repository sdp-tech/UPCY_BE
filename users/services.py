import os
from typing import Dict

from boto3 import client
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from users.models.user import User


class UserService:
    def __init__(self):
        pass

    @staticmethod
    def user_sign_up(user_data: Dict) -> None:
        """
        사용자 회원가입 함수
        """
        try:
            if User.objects.filter(email=user_data["email"]).exists():
                # 이메일 중복 확인
                raise ValidationError("A user with this email already exists.")

            # 사용자 생성
            user = User.objects.create_user(**user_data)
            user.save()

        except ValidationError as e:
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise Exception(f"An error occurred during sign-up: {str(e)}")

    @staticmethod
    def login(email: str, password: str) -> Dict:
        """
        사용자 로그인 함수 -> 로그인 성공 시 AccessToken, RefreshToken 발급
        """
        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError("User with this email does not exist.")

        if not check_password(password, user.password):
            raise ValidationError("아이디나 비밀번호가 올바르지 않습니다.")

        # 마지막 로그인 시간 업데이트
        user.last_login = timezone.now()
        user.save()

        # JWT 토큰 발급
        token = RefreshToken.for_user(user=user)
        data = {"access": str(token.access_token), "refresh": str(token)}

        return data

    @staticmethod
    def logout(refresh_token: str) -> None:
        """
        로그아웃 처리 함수
        """
        try:
            # Refresh token 유효성 검사 및 블랙리스트 처리
            token = RefreshToken(refresh_token)
            token.blacklist()  # 블랙리스트에 추가하여 사용 불가 처리
        except (TokenError, InvalidToken) as e:
            raise ValidationError("Invalid or expired token.")
        except Exception as e:
            raise Exception(f"An error occurred during logout: {str(e)}")

    @staticmethod
    def delete_user(user: User, password: str) -> bool:
        """
        사용자 삭제하는 함수 (회원탈퇴 시 사용함)
        """
        try:
            if not password:
                raise ValidationError("비밀번호 필드에 공백이 입력되었습니다.")

            if not check_password(password, user.password):
                raise ValidationError("비밀번호가 올바르지 않습니다.")

            with transaction.atomic():
                s3 = client("s3")
                if user.profile_image and user.profile_image.name:
                    # S3에서 프로필 이미지 삭제
                    s3.delete_object(
                        Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                        Key=user.profile_image.name,
                    )
                # 사용자 삭제
                user.delete()
                return True
        except ValidationError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise Exception(f"An error occurred while deleting the user: {str(e)}")

    @staticmethod
    def update_user_role(user: User, role: str) -> None:
        """
        User Role 변경하는 함수
        """
        try:
            user.role = role
            user.save()
        except Exception as e:
            raise Exception(f"An error occurred while updating the user role: {str(e)}")

    @staticmethod
    @transaction.atomic
    def upload_user_profile_image(user: User, image_file) -> None:
        """
        사용자 프로필 이미지를 S3에 업로드하는 함수
        """
        try:
            # 이미지 크기 확인
            if image_file.size > 10 * 1024 * 1024:
                raise ValidationError("Image file size must be less than 10MB")

            # 기존 프로필 이미지 삭제 후 새 이미지 저장
            if user.profile_image:
                user.profile_image.delete(save=False)

            user.profile_image = image_file
            user.save()
            print("Successfully uploaded profile image")
        except ValidationError as e:
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise Exception(
                f"An error occurred while uploading the profile image: {str(e)}"
            )
