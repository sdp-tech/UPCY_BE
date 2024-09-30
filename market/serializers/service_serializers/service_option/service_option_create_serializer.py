from rest_framework import serializers

from market.models import Service, ServiceOption


class ServiceOptionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceOption
        fields = ["option_name", "option_content", "option_price"]

    def validate(self, attrs):
        service: Service = self.context.get("service")
        if service.service_option.filter(
            option_name=attrs.get("option_name")
        ).exists():  # 역참조 (related_name)
            raise serializers.ValidationError("Option already exists")

        if attrs.get("option_price") is not None and attrs.get("option_price") < 0:
            raise serializers.ValidationError("Option price must be greater than 0")

        return attrs

    def create(self, validated_data):
        service: Service = self.context.get("service")
        service_option = ServiceOption.objects.create(
            market_service=service, **validated_data  # 역참조
        )
        service_option.save()
        return service_option
