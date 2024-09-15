from django.urls import path

from users.views.reformer_view import ReformerProfileView
from users.views.token_view import *
from users.views.user_auth_view import *

app_name = "users"

urlpatterns =[
    path('/signup', UserSignUpApi.as_view(), name='user_crud'),
    path('/login', UserLoginApi.as_view(), name='login'),
    path('/logout', UserLogoutApi.as_view(), name='logout'),
    path('/token/verify', UserTokenVerifyView.as_view(), name='token_verify'),
    path('/token/refresh', UserTokenRefreshView.as_view(), name='token_refresh'),
    path('/reformer', ReformerProfileView.as_view(), name='reformer'),
]