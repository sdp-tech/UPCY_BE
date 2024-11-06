from rest_framework import serializers
from market.models import ServiceStyle


class ServiceStyleRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStyle
        fields = ['style_uuid', 'style_name']
