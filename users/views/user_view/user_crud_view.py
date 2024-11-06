from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from users.serializers.user_serializer.user_information_serializer import \
    UserInformationSerializer
from users.serializers.user_serializer.user_update_serializer import \
    UserUpdateSerializer
from users.services import UserService


class UserCrudApi(APIView):
    permission_classes = [IsAuthenticated]
    service = UserService()

    def get(self, request) -> Response:
        try:
            serializer = UserInformationSerializer(
                instance=request.user, context={"request": request}
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        serializer = UserUpdateSerializer(
            data=request.data, instance=request.user, partial=True
        )
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    data={"message": "Successfully updated user information"},
                    status=status.HTTP_200_OK,
                )
        except ValidationError as e:
            return Response(data=e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request) -> Response:
        user = request.user #사용자 정보를 request에서 가져옴
        refresh_token = request.data.get("refresh")
        password = request.data.get("password")
        if not refresh_token:
            return Response(
                data={"message": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            self.service.logout(refresh_token=refresh_token)  # Refresh Token 만료 처리
            if self.service.delete_user(user, password):  # 사용자 삭제
                return Response(
                    data={"message": "Successfully deleted user"},
                    status=status.HTTP_200_OK,
                )
            else:
                raise Exception
        except (TokenError, InvalidToken) as e:
            return Response(
                data={"message": f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    service = UserService()

    def post(self, request) -> Response:
        user = request.user
        image_file = request.FILES.get(
            "profile_image"
        )  # 이미지 파일 request body에서 획득
        if not image_file:
            return Response(
                data={"message": "Profile image is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self.service.upload_user_profile_image(user=user, image_file=image_file)
            return Response(
                data={"message": "Successfully uploaded profile image"},
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response(
                data={"message": f"Validation Error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                data={"message": f"Exception: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
