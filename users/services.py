from typing import Dict

from rest_framework import exceptions
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

from users.models import User
from users.selectors import UserSelector


class UserService:
    def __init__(self):
        pass

    @staticmethod
    def user_sign_up(user_data: Dict) -> None:
        """
        사용자 회원가입 함수
        """
        try:
            if User.objects.filter(email=user_data["email"]).exists(): # email에 해당하는 사용자가 이미 존재하는지 확인
                raise ValidationError('A user with this email already exists.')

            # 없으면 생성
            user = User.objects.create_user(
                email=user_data["email"],
                password=user_data["password"],
                agreement_terms=user_data["agreement_terms"],
                address=user_data["address"],
                nickname=user_data["nickname"],
                phone=user_data["phone"]
            )
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
        """
        로그아웃 처리 함수
        """
        try:
            # refresh token 유효성 검사 및 블랙리스트 처리
            token = RefreshToken(refresh_token)
            token.blacklist()  # 블랙리스트에 추가하여 사용 불가 처리
        except (TokenError, InvalidToken) as e:
            raise e
        except Exception as e:
            raise e

    @staticmethod
    def delete_user(user: User) -> None:
        """
        사용자 삭제하는 함수 (회원탈퇴 시 사용함)
        """
        try:
            user.delete()
        except Exception as e:
            raise e

    @staticmethod
    def update_user_role(user: User, role: str) -> None:
        """
        User Role 변경하는 함수
        """
        try:
            user.role = role
            user.save()
        except Exception as e:
            raise e

    @staticmethod
    @transaction.atomic
    def upload_user_profile_image(user: User, image_file) -> None:
        """
        사용자 프로필 이미지를 S3에 업로드하는 함수
        """
        try:
            if image_file.size > 10 * 1024 * 1024: # 10MB 이상의 프로필 이미지는 안됨!
                raise ValidationError("Image file size must be less than 10MB")

            if user.profile_image: # 기존 프로필 이미지 제거 후 교체해줘야 함
                user.profile_image.delete(save=False)

            user.profile_image = image_file
            user.save()
            print("Successfully uploaded profile image")
        except ValidationError as e:
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise e

