from django.urls import path, re_path, include

urlpatterns = [
    path('api/core', include('core.urls')),
    path('api/user', include('users.urls')),
    path('api/products',include('products.urls')),
    path('api/services',include('services.urls')),
]
