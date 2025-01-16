from rest_framework import serializers

from order.models import DeliveryInformation


class DeliveryStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryInformation
        fields = "__all__"
