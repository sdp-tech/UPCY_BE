from rest_framework import serializers

from order.models import DeliveryInformation


class DeliveryInformationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryInformation
        fields = [
            "delivery_company",
            "delivery_tracking_number",
        ]

    def validate(self, attrs):
        if (
            attrs.get("delivery_tracking_number") is not None
            and attrs.get("delivery_tracking_number") < 0
        ):
            raise serializers.ValidationError(
                "delivery_tracking_number must be greater than 0"
            )

        return attrs

    def update(self, instance, validated_data):
        instance.delivery_company = validated_data.get(
            "delivery_company", instance.delivery_company
        )
        instance.delivery_tracking_number = validated_data.get(
            "delivery_tracking_number", instance.delivery_tracking_number
        )

        instance.save()
        return instance