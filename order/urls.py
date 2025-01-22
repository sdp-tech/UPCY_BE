from django.urls import path

from order.views.order_view import *

urlpatterns = [
    path("", OrderView.as_view(), name="order"),
    path("/services/<uuid:service_uuid>", ServiceOrderListView.as_view(), name="service_order_list"),
]
