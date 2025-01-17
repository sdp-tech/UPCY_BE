from rest_framework import serializers

from order.models import DeliveryInformation


class DeliveryStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryInformation
        fields = [
            "delivery_company",
            "delivery_tracking_number",
            "delivery_address",
            "delivery_name",
            "delivery_phone_number",
        ]
