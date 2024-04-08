from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import UserSignUpApi,UserLoginApi,ReformerProfileApi,CertificationCreateApi
app_name = "users"

urlpatterns =[
    # path("reformer_signup/", ReformerSignUpApi.as_view(), name = "reformer_signup"),
    # path("consumer_signup/", ConsumerSignUpApi.as_view(), name = "consumer_signup"),
    path('signup/',UserSignUpApi.as_view(),name='signup'),
    path('login/', UserLoginApi.as_view(), name = 'login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile_register/',ReformerProfileApi.as_view(),name='profile_register'),   
    path('certification_register/',CertificationCreateApi.as_view(),name='certification'),
]