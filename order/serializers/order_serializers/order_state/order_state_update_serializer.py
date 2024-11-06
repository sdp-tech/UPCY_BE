from rest_framework import serializers
from order.models import OrderState

class OrderStateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderState
        fields = [
            "reformer_status",
        ]

    def validate(self, value):
        # 허용된 값인지 검증합니다.
        valid_statuses = [choice[0] for choice in OrderState._meta.get_field('reformer_status').choices]
        if value not in valid_statuses:
            raise serializers.ValidationError("유효하지 않은 상태 값입니다.")
        return value

    def update(self, instance, validated_data):
        instance.reformer_status = validated_data.get("reformer_status", instance.reformer_status)
        instance.save()
        return instance