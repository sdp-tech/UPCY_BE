from django.urls import path
from .views import *

app_name = "services"

urlpatterns = [
    path('create/',ServiceCreateApi.as_view(),name='service_create'),
    path('photos/create/',ServicePhotoCreateApi.as_view(), name='service_photo_create'),

]