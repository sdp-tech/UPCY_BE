from rest_framework import serializers

from market.serializers.service_serializers.service_material.service_material_retrieve_serializer import (
    ServiceMaterialRetrieveSerializer,
)
from market.serializers.service_serializers.service_option.service_option_retrieve_serializer import (
    ServiceOptionRetrieveSerializer,
)
from order.models import Order
from order.serializers.order_create_serializer import OrderImageSerializer
from order.serializers.order_status_serializer import OrderStatusSerailzier
from order.serializers.orderer_information_serializer import (
    OrdererInformationSerializer,
)
from order.serializers.transaction_serializer import TransactionSerializer
from users.serializers.user_serializer.user_information_serializer import (
    UserOrderInformationSerializer,
)


class OrderRetrieveSerializer(serializers.ModelSerializer):
    service_uuid = serializers.SerializerMethodField(read_only=True)
    materials = ServiceMaterialRetrieveSerializer(many=True, read_only=True)
    additional_options = ServiceOptionRetrieveSerializer(many=True, read_only=True)
    order_status = OrderStatusSerailzier(many=True, read_only=True)
    orderer_information = serializers.SerializerMethodField(read_only=True)
    transaction = TransactionSerializer(read_only=True)
    images = OrderImageSerializer(source="order_image", many=True, read_only=True)

    def get_service_uuid(self, obj):
        return obj.service.service_uuid

    def get_orderer_information(self, obj):
        if hasattr(obj, "orderer_information"):
            return OrdererInformationSerializer(obj.orderer_information).data
        return UserOrderInformationSerializer(obj.orderer).data

    class Meta:
        model = Order
        fields = [
            "service_uuid",
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
            "images",
            "created",
        ]
