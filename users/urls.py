from django.urls import path

from users.views.reformer_view import ReformerProfileView
from users.views.token_view import *
from users.views.user_auth_view import *
from users.views.user_crud_view import *

app_name = "users"

urlpatterns =[
    path('', UserCrudApi.as_view(), name='user_crud'),
    path('/signup', UserSignUpApi.as_view(), name='signup'),
    path('/login', UserLoginApi.as_view(), name='login'),
    path('/logout', UserLogoutApi.as_view(), name='logout'),
    path('/token/verify', UserTokenVerifyView.as_view(), name='token_verify'),
    path('/token/refresh', UserTokenRefreshView.as_view(), name='token_refresh'),
    path('/reformer', ReformerProfileView.as_view(), name='reformer'),
    path('/profile-image', UserImageUploadView.as_view(), name='upload_profile_image'),
]