from rest_framework import serializers

from market.models import ServiceOption, ServiceOptionImage


class ServiceOptionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOptionImage
        fields = ["image"]

class ServiceOptionRetrieveSerializer(serializers.ModelSerializer):
    service_option_image = ServiceOptionImageSerializer(many=True)

    class Meta:
        model = ServiceOption
        fields = ["option_uuid", "option_name", "option_content", "option_price", "service_option_image"]
