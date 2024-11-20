from rest_framework import serializers

from order.models import DeliveryInformation


class DeliveryInformationRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryInformation
        fields = ["delivery_company", "delivery_tracking_number"]