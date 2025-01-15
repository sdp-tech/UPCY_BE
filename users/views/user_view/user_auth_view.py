import logging

from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from core.exceptions import view_exception_handler
from users.models.user import User
from users.serializers.user_serializer.user_login_serializer import UserLoginSerializer
from users.serializers.user_serializer.user_signup_serializer import (
    UserSignUpSerializer,
)
from users.services import UserService

logger = logging.getLogger(__name__)


class UserSignUpApi(APIView):
    permission_classes = [AllowAny]

    @view_exception_handler
    def post(self, request):
        logger.info(request.data)
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        UserService.user_sign_up(data)

        return Response(
            {
                "message": "Success",
            },
            status=status.HTTP_201_CREATED,
        )


class UserLoginApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data
            service = UserService()
            login_data = service.login(
                email=data.get("email"),
                password=data.get("password"),
            )
            return Response(data=login_data, status=status.HTTP_200_OK)
        except User.DoesNotExist as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserLogoutApi(APIView):
    permission_classes = [IsAuthenticated]
    service = UserService()

    def post(self, request):
        # request body에서 refresh token 획득
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                data={"message": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            # logout
            self.service.logout(refresh_token=refresh_token)
            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except (TokenError, InvalidToken):
            return Response(
                data={"message": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
