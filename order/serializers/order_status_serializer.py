from rest_framework import serializers

from order.models import OrderStatus


class OrderStatusRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderStatus
        fields = ["status", "created"]


class OrderStatusRejectedSerailzier(serializers.ModelSerializer):
    rejected_reason = serializers.SerializerMethodField(read_only=True)

    def get_rejected_reason(self, obj):
        return obj.order.rejected_reason

    class Meta:
        model = OrderStatus
        fields = ["status", "rejected_reason", "created"]
