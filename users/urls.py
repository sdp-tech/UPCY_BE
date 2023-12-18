from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import ReformerSignUpApi
app_name = "users"

urlpatterns =[
    path("reformer_signup/", ReformerSignUpApi.as_view(), name = "reformer_signup"),
]