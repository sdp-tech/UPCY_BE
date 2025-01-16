from rest_framework import serializers

from order.models import OrderStatus


class OrderStatusSerailzier(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ["status", "created"]
