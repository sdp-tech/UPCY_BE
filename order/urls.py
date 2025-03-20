from django.urls import path

from order.views.order_view import *

urlpatterns = [
    path("", OrderView.as_view(), name="order"),
    path(
        "/services/<uuid:service_uuid>",
        ServiceOrderListView.as_view(),
        name="service_order_list",
    ),
    path(
        "/<uuid:order_uuid>/status",
        OrderStatusView.as_view(),
        name="order_update",
    ),
    path(
        "/transactions/<uuid:transaction_uuid>/delivery",
        DeliveryInformationUpdateView.as_view(),
        name="delivery_update",
    ),
]
