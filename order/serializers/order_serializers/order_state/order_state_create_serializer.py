from rest_framework import serializers
from order.models import OrderState

class OrderStateCreateSerializer(serializers.ModelSerializer):
    orderState_uuid = serializers.UUIDField(read_only=True)
    class Meta:
        model = OrderState
        fields = [
            "orderState_uuid",
            "reformer_status",
        ]

    def create(self, validated_data):
        order_state = OrderState.objects.create(
            service_order=self.context.get("service_order")
            ,**validated_data)
        order_state.save()
        return order_state