from django.urls import path
from .views import *

app_name = "products"

urlpatterns = [
    path('create/',ProductCreateApi.as_view(),name='product_create'),
    path('photos/create/',ProductPhotoCreateApi.as_view(), name='product_photo_create'),
    path('',ProductListApi.as_view(),name='product_list'),
    path('<int:product_id>/like/',ProductLikeApi.as_view(), name='product_like'),
]
