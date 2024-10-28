from rest_framework import serializers
from order.models import OrderState

class OrderStateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderState
        fields = [
            "reformer_status",
        ]

    def update(self, instance, validated_data):
        instance.reformer_status = validated_data.get("reformer_status", instance.reformer_status)
        instance.save()
        return instance