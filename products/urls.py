from django.urls import path
from .views import *

app_name = "products"


urlpatterns = [
    path('create/',ProductCreateApi.as_view(),name='product_create'),
    
]
