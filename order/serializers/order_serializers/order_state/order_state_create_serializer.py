from rest_framework import serializers

from order.models import OrderState


class OrderStateCreateSerializer(serializers.ModelSerializer):
    order_state_uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = OrderState
        fields = [
            "order_state_uuid",
            "reformer_status",
        ]

    def validate(self, value):
        valid_statuses = [
            choice[0]
            for choice in OrderState._meta.get_field("reformer_status").choices
        ]
        if value not in valid_statuses:
            raise serializers.ValidationError("유효하지 않은 상태 값입니다.")
        return value

    def create(self, validated_data):
        order_state = OrderState.objects.create(
            service_order=self.context.get("service_order"), **validated_data
        )
        order_state.save()
        return order_state