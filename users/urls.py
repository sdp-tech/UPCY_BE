from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import *
app_name = "users"

urlpatterns =[
    # path("reformer_signup/", ReformerSignUpApi.as_view(), name = "reformer_signup"),
    # path("consumer_signup/", ConsumerSignUpApi.as_view(), name = "consumer_signup"),
    path('signup',UserSignUpApi.as_view(),name='signup'),
    path('login', UserLoginApi.as_view(), name = 'login'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('reformer/profile',ReformerProfileApi.as_view(),name='reformer_profile_register'),
    path('reformer/profile/certification',CertificationCreateApi.as_view(),name='certification'),
    path('reformer/profile/competition',CompetitionCreateApi.as_view(),name='competition'),
    path('reformer/profile/intership',IntershipCreateApi.as_view(),name='intership'),
    path('reformer/profile/freelancer',FreelancerCreateApi.as_view(),name='freelancer'),
    path('reformer/profile/<int:user_id>',ReformerProfileDetailApi.as_view(),name='reformer_profile'),
    path('profile/img',UserProfileImageApi.as_view(),name='profile_img'),
    path('profile',UserDetailApi.as_view(),name='profile'),
]