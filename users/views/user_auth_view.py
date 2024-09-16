from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from users.serializers.user_login_serializer import UserLoginSerializer
from users.serializers.user_signup_serializer import UserSignUpSerializer
from users.services import UserService


class UserSignUpApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            requested_data = UserSignUpSerializer(data=request.data)
            if requested_data.is_valid(raise_exception=True):
                data = requested_data.validated_data

                UserService.user_sign_up(data)
                return Response(
                    {
                        'message': 'success',
                    },
                    status=status.HTTP_201_CREATED
                )
        except ValidationError as e:
            return Response(
                data={
                    'message': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserLoginApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        requested_data = UserLoginSerializer(data=request.data)
        if requested_data.is_valid(raise_exception=True):
            data = requested_data.validated_data
            service = UserService()
            try:
                login_data = service.login(
                    email=data.get('email'),
                    password=data.get('password'),
                )
                return Response(
                    data=login_data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    data={
                        'message': str(e)
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            data={
                'message': 'Invalid input data. check API documentation'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class UserLogoutApi(APIView):
    permission_classes = [IsAuthenticated]
    service = UserService()

    def post(self, request):
        # request body에서 refresh token 획득
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                data={"message": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # logout
            self.service.logout(refresh_token=refresh_token)
            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT
            )
        except (TokenError, InvalidToken):
            return Response(
                data={"message": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
