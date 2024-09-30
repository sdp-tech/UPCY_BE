from rest_framework import serializers

from market.models import ServiceOption


class ServiceOptionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOption
        fields = ["option_name", "option_content", "option_price"]
        extra_kwargs = {
            "option_name": {"required": False},
            "option_content": {"required": False},
            "option_price": {"required": False},
        }

    def validate(self, attrs):
        if attrs.get("option_name") is not None or attrs.get("option_name") == "":
            raise serializers.ValidationError("option name is required")

        if attrs.get("option_name") == self.instance.option_name:
            raise serializers.ValidationError("option name must be different")

        if attrs.get("option_price") is not None and attrs.get("option_price") < 0:
            raise serializers.ValidationError("option price must be greater than 0")

        return attrs

    def update(self, instance, validated_data):
        instance.option_name = validated_data.get("option_name", instance.option_name)
        instance.option_content = validated_data.get(
            "option_content", instance.option_content
        )
        instance.option_price = validated_data.get(
            "option_price", instance.option_price
        )
        instance.save()
        return instance
