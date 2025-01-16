from rest_framework import serializers

from order.models import Transaction
from order.serializers.delivery_status_serializer import DeliveryStatusSerializer


class TransactionSerializer(serializers.ModelSerializer):

    delivery_status = DeliveryStatusSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ["transaction_uuid", "transaction_option", "delivery_status"]
