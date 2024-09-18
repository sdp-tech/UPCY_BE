from django.urls import include, path

urlpatterns = [
    path('api/core', include('core.urls')),
    path('api/user', include('users.urls')),
    path('api/service',include('market.urls')),
    path('api/order', include('order.urls'))
]
