from django.urls import include, path

urlpatterns = [
    path("api/core", include("core.urls")),
    path("api/user", include("users.urls")),
    path("api/market", include("market.urls")),
    path("api/orders", include("order.urls")),
]
