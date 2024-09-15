from django.urls import include, path

urlpatterns = [
    path('api/core', include('core.urls')),
    path('api/user', include('users.urls')),
    path('api/products',include('products.urls')),
    path('api/services',include('services.urls')),
]
