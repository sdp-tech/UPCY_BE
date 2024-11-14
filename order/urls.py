from django.urls import path

from order.views.image_upload_view import OrderAdditionalImageView, OrderImageView
from order.views.order_delivery_information.order_delivery_view import (
    OrderDeliveryCreateView,
    OrderDeliveryView,
)
from order.views.order_state.order_state_view import (
    OrderStateCreateView,
    OrderStateView,
)
from order.views.order_transaction.order_transaction_view import (
    OrderTransactionOptionCreateView,
    OrderTransactionOptionView,
)
from order.views.order_view.customer_order_view.order_crud_view import OrderCrudView
from order.views.order_view.customer_order_view.order_list_view import (
    GetCustomerAllOrderView,
    OrderCreateListView,
)
from order.views.order_view.reformer_order_view.order_list_view import (
    GetReformerAllOrderView,
)
from order.views.order_view.reformer_order_view.order_update_view import OrderUpdateView

urlpatterns = [
    path("/<uuid:order_uuid>/", OrderCrudView.as_view(), name="customer_order_crud"),
    path("/customer", OrderCreateListView.as_view(), name="customer_order_create_list"),
    path(
        "/customer/view",
        GetCustomerAllOrderView.as_view(),
        name="customer_order_list_without_order_uuid",
    ),
    path(
        "/<uuid:order_uuid>/transaction/<uuid:transaction_uuid>/view",
        OrderTransactionOptionView.as_view(),
        name="order_transaction_view",
    ),
    path(
        "/<uuid:order_uuid>/transaction/<uuid:transaction_uuid>/update",
        OrderTransactionOptionCreateView.as_view(),
        name="order_transaction_update",
    ),
    path(
        "/<uuid:order_uuid>/state/<uuid:state_uuid>/view",
        OrderStateView.as_view(),
        name=" order_state_view",
    ),
    path(
        "/<uuid:order_uuid>/state/<uuid:state_uuid>/update",
        OrderStateCreateView.as_view(),
        name="order_state_update",
    ),
    path(
        "/<uuid:order_uuid>/delivery/<uuid:delivery_uuid>/view",
        OrderDeliveryView.as_view(),
        name="order_delivery_view",
    ),
    path(
        "/<uuid:order_uuid>/delivery/<uuid:delivery_uuid>/update",
        OrderDeliveryCreateView.as_view(),
        name="order_delivery_update",
    ),
    path(
        "/reformer/view", GetReformerAllOrderView.as_view(), name="reformer_order_list"
    ),
    path(
        "/reformer/<uuid:order_uuid>/update",
        OrderUpdateView.as_view(),
        name="reformer_order_update",
    ),
    path(
        "/customer/<uuid:order_uuid>/image",
        OrderImageView.as_view(),
        name="customer_order_image_upload",
    ),
    path(
        "/customer/<uuid:order_uuid>/additional/image/<uuid:additional_uuid>",
        OrderAdditionalImageView.as_view(),
        name="customer_order_additional_image_upload",
    ),
]
