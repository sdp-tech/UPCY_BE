from rest_framework import serializers

from market.serializers.service_serializers.service_create_retrieve_serializer import (
    ServiceRetrieveSerializer,
)
from market.serializers.service_serializers.service_material.service_material_retrieve_serializer import (
    ServiceMaterialRetrieveSerializer,
)
from market.serializers.service_serializers.service_option.service_option_retrieve_serializer import (
    ServiceOptionRetrieveSerializer,
)
from order.models import Order
from order.serializers.delivery_status_serializer import DeliveryStatusSerializer
from order.serializers.order_create_serializer import OrderImageSerializer
from order.serializers.order_status_serializer import OrderStatusRetrieveSerializer
from order.serializers.orderer_information_serializer import (
    OrdererInformationSerializer,
)
from order.serializers.transaction_serializer import TransactionSerializer
from users.serializers.user_serializer.user_information_serializer import (
    UserOrderInformationSerializer,
)


class OrderRetrieveSerializer(serializers.ModelSerializer):
    service_info = serializers.SerializerMethodField(read_only=True)
    materials = ServiceMaterialRetrieveSerializer(many=True, read_only=True)
    additional_options = ServiceOptionRetrieveSerializer(many=True, read_only=True)
    order_status = OrderStatusRetrieveSerializer(many=True, read_only=True)
    orderer_information = serializers.SerializerMethodField(read_only=True)
    transaction = TransactionSerializer(read_only=True)
    delivery_status = serializers.SerializerMethodField(read_only=True)
    images = OrderImageSerializer(source="order_image", many=True, read_only=True)

    def get_service_info(self, obj):
        return ServiceRetrieveSerializer(obj.service).data

    def get_orderer_information(self, obj):
        # 만약, 기본 사용자 정보가 아닌, 새로운 사용자 정보를 기입하여 주문한 경우는, User 정보가 아니라, OrdererInformation 정보를 반환
        if hasattr(obj, "orderer_information"):
            return OrdererInformationSerializer(obj.orderer_information).data
        return UserOrderInformationSerializer(obj.orderer).data

    def get_delivery_status(self, obj):
        delivery_information = obj.transaction.delivery_information
        if delivery_information.exists():
            return DeliveryStatusSerializer(delivery_information.first()).data
        return None

    class Meta:
        model = Order
        fields = [
            "service_info",
            "order_uuid",
            "order_date",
            "orderer_information",
            "service_price",
            "option_price",
            "total_price",
            "materials",
            "additional_options",
            "extra_material",
            "additional_request",
            "order_status",
            "transaction",
            "delivery_status",
            "images",
            "created",
        ]
