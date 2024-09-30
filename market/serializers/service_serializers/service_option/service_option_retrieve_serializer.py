from rest_framework import serializers

from market.models import ServiceOption


class ServiceOptionRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOption
        fields = ["option_uuid", "option_name", "option_content", "option_price"]
