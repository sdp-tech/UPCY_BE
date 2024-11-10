from django.urls import path

from users.views.reformer_view.reformer_education_view.reformer_education_create_list_view import (
    ReformerEducationCreateListView,
)
from users.views.reformer_view.reformer_education_view.reformer_education_document_view import (
    ReformerEducationDocumentView,
)
from users.views.reformer_view.reformer_education_view.reformer_education_view import (
    ReformerEducationView,
)
from users.views.reformer_view.reformer_profile_view import ReformerProfileView
from users.views.token_view.token_view import UserTokenRefreshView, UserTokenVerifyView
from users.views.user_view.user_auth_view import *
from users.views.user_view.user_crud_view import *

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
