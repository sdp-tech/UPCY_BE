from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import ReformerSignUpApi, ConsumerSignUpApi, UserLoginApi
app_name = "users"

urlpatterns =[
    path("reformer_signup/", ReformerSignUpApi.as_view(), name = "reformer_signup"),
    path("consumer_signup/", ConsumerSignUpApi.as_view(), name = "consumer_signup"),
    path('login/', UserLoginApi.as_view(), name = 'login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]