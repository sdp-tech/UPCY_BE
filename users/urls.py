from django.urls import path
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import authenticate

from users.views.reformer_view.reformer_education_view.reformer_education_create_list_view import \
    ReformerEducationCreateListView
from users.views.reformer_view.reformer_education_view.reformer_education_document_view import \
    ReformerEducationDocumentView
from users.views.reformer_view.reformer_education_view.reformer_education_view import \
    ReformerEducationView
from users.views.reformer_view.reformer_profile_view import ReformerProfileView
from users.views.token_view.token_view import (UserTokenRefreshView,
                                               UserTokenVerifyView)
from users.views.user_view.user_auth_view import *
from users.views.user_view.user_crud_view import *
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
        user = request.user
        refresh_token = request.data.get("refresh")
        password = request.data.get("password")

        if not refresh_token:
            return Response(
                data={"message": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not password:
            return Response(
                data={"message": "Password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not authenticate(username=user.username, password=password):
            return Response(
                data={"message": "Invalid password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self.service.logout(refresh_token=refresh_token)
            if self.service.delete_user(user):
                return Response(
                    data={"message": "Successfully deleted user"},
                    status=status.HTTP_200_OK,
                )
            else:
                raise Exception("Failed to delete user.")
        except (TokenError, InvalidToken) as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


app_name = "users"

urlpatterns = [
    path("", UserCrudApi.as_view(), name="user_crud"),
    path("/signup", UserSignUpApi.as_view(), name="signup"),
    path("/login", UserLoginApi.as_view(), name="login"),
    path("/logout", UserLogoutApi.as_view(), name="logout"),
    path("/token/verify", UserTokenVerifyView.as_view(), name="token_verify"),
    path("/token/refresh", UserTokenRefreshView.as_view(), name="token_refresh"),
    path("/reformer", ReformerProfileView.as_view(), name="reformer"),
    path(
        "/reformer/education",
        ReformerEducationCreateListView.as_view(),
        name="reformer_education",
    ),
    path(
        "/reformer/education/<uuid:education_uuid>",
        ReformerEducationView.as_view(),
        name="reformer_education_detail",
    ),
    path(
        "/reformer/education/<uuid:education_uuid>/document",
        ReformerEducationDocumentView.as_view(),
        name="reformer_education_document",
    ),
    path("/profile-image", UserImageUploadView.as_view(), name="upload_profile_image"),
]
