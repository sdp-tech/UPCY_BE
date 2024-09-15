from typing import Dict

from rest_framework import exceptions
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.selectors import UserSelector


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
        try:
            user.delete()
        except Exception as e:
            raise e

    @staticmethod
    def update_user_role(user: User, role: str) -> None:
        try:
            user.role = role
            user.save()
        except Exception as e:
            raise e
