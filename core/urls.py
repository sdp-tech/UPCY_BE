from django.urls import path

from core.views import HealthCheckView

urlpatterns = [
    path("/health-check", HealthCheckView.as_view(), name="health_check"),
]
