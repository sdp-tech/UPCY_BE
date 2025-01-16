from django.urls import path

from order.views.order_view import OrderView

urlpatterns = [
    path("", OrderView.as_view(), name="order"),
]
