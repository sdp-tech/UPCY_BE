from django.urls import path
from .views import *

app_name = "services"

urlpatterns = [
    path('create/',ServiceCreateApi.as_view(),name='service_create'),
    path('photos/create/',ServicePhotoCreateApi.as_view(), name='service_photo_create'),
    path('',ServiceListApi.as_view(),name='service_list'),
    path('<int:service_id>/like/',ServiceLikeApi.as_view(), name='service_like'),
    path('<int:service_id>/', ServiceDetailApi.as_view(), name='service_detail'),
    path('<int:service_id>/update/',ServiceUpdateApi.as_view(),name='service_update'),
]