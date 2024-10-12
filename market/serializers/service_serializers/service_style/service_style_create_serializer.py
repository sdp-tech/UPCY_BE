from rest_framework import serializers
from market.models import ServiceStyle


class ServiceStyleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStyle
        fields = ['style_name', 'description', 'price', 'available']

    def create(self, validated_data):
        service_style = ServiceStyle.objects.create(**validated_data)
        return service_style

    def validate_style_name(self, value):

        if ServiceStyle.objects.filter(style_name=value).exists():
            raise serializers.ValidationError("해당 스타일 이름은 이미 존재합니다.")
        return value
