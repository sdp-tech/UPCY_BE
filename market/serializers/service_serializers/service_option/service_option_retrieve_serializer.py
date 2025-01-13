from rest_framework import serializers

from market.models import ServiceOption, ServiceOptionImage


class ServiceOptionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOptionImage
        fields = ["image"]


class ServiceOptionRetrieveSerializer(serializers.ModelSerializer):
    service_option_images = serializers.SerializerMethodField()

    def get_service_option_images(self, obj):
        return ServiceOptionImageSerializer(
            instance=obj.service_option_image, many=True
        ).data

    class Meta:
        model = ServiceOption
        fields = [
            "option_uuid",
            "option_name",
            "option_content",
            "option_price",
            "service_option_images",
        ]
