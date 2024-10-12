from rest_framework import serializers
from market.models import ServiceStyle


class ServiceStyleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStyle
        fields = ['style_name']

    def validate(self, attrs):
        return attrs

    def update(self, instance, validated_data):
        instance.style_name = validated_data.get('style_name', instance.style_name)
        instance.save()
        return instance
