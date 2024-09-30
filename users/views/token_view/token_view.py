from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


class UserTokenVerifyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                data={"message": "Authorization header missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = auth_header.split(" ")[-1]

        try:
            # AccessToken을 통해 토큰 검증
            AccessToken(access_token)
            return Response(
                data={"message": "Access token is valid."}, status=status.HTTP_200_OK
            )
        except (InvalidToken, TokenError):
            return Response(
                data={"message": "Invalid access token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class UserTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                data={"message": "Refresh token not found in body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh_token = RefreshToken(refresh_token)
            new_access_token = refresh_token.access_token
            return Response(
                data={"access": str(new_access_token), "refresh": str(refresh_token)}
            )
        except (InvalidToken, TokenError) as e:
            return Response(
                data={"message": f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
