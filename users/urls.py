from django.urls import path
from users.views.reformer_view.reformer_career_view.reformer_career_create_list_view import \
    ReformerCareerCreateListView
from users.views.reformer_view.reformer_career_view.reformer_career_document_view import \
    ReformerCareerDocumentView
from users.views.reformer_view.reformer_career_view.reformer_career_view import \
    ReformerCareerView
from users.views.reformer_view.reformer_awards_view.reformer_awards_create_list_view import \
    ReformerAwardsCreateListView
from users.views.reformer_view.reformer_awards_view.reformer_awards_document_view import \
    ReformerAwardsDocumentView
from users.views.reformer_view.reformer_awards_view.reformer_awards_view import \
    ReformerAwardsView
from users.views.reformer_view.reformer_certification_view.reformer_certification_create_list_view import \
    ReformerCertificationCreateListView
from users.views.reformer_view.reformer_certification_view.reformer_certification_document_view import \
    ReformerCertificationDocumentView
from users.views.reformer_view.reformer_certification_view.reformer_certificaton_view import \
    ReformerCertificationView
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
    path(
        "/reformer/certification",
        ReformerCertificationCreateListView.as_view(),
        name="reformer_certification",
    ),
    path(
        "/reformer/certification/<uuid:certification_uuid>",
        ReformerCertificationView.as_view(),
        name="reformer_certification_detail",
    ),
    path(
        "/reformer/certification/<uuid:certification_uuid>/document",
        ReformerCertificationDocumentView.as_view(),
        name="reformer_certification_document",
    ),
    path(
        "/reformer/awards",
        ReformerAwardsCreateListView.as_view(),
        name="reformer_awards",
    ),
    path(
        "/reformer/awards/<uuid:award_uuid>",
        ReformerAwardsView.as_view(),
        name="reformer_awards_detail",
    ),
    path(
        "/reformer/awards/<uuid:award_uuid>/document",
        ReformerAwardsDocumentView.as_view(),
        name="reformer_awards_document",
    ),
    path(
        "/reformer/career",
        ReformerCareerCreateListView.as_view(),
        name="reformer_career",
    ),
    path(
        "/reformer/career/<uuid:career_uuid>",
        ReformerCareerView.as_view(),
        name="reformer_career_detail",
    ),
    path(
        "/reformer/career/<uuid:career_uuid>/document",
        ReformerCareerDocumentView.as_view(),
        name="reformer_career_document",
    ),
    path("/profile-image", UserImageUploadView.as_view(), name="upload_profile_image"),
]
