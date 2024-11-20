from rest_framework import serializers

from order.models import DeliveryInformation


class DeliveryInformationCreateSerializer(serializers.ModelSerializer):
    delivery_uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = DeliveryInformation
        fields = [
            "delivery_uuid",
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

    def create(self, validated_data):
        order_delivery_information = DeliveryInformation.objects.create(
            service_order=self.context.get("service_order"), **validated_data
        )

        order_delivery_information.save()

        return order_delivery_information