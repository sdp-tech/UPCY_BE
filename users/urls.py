from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *
app_name = "users"

urlpatterns =[
    path('/signup',UserSignUpApi.as_view(),name='signup'),
    path('/login', UserLoginApi.as_view(), name = 'login'),
    path('/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    path('/reformer', ReformerProfileCreateView.as_view(), name='create_reformer_profile'),
]