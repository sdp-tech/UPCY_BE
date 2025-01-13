from rest_framework import serializers

from market.models import Service


class ServiceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "service_title",
            "service_content",
            "service_category",
            "service_period",
            "basic_price",
            "max_price",
            "suspended",
        ]
        extra_kwargs = {
            "service_title": {"required": False},
            "service_content": {"required": False},
            "service_category": {"required": False},
            "service_period": {"required": False},
            "basic_price": {"required": False},
            "max_price": {"required": False},
            "suspended": {"required": False},
        }

    def validate(self, attrs):
        if len(attrs.keys()) == 0:
            raise serializers.ValidationError("No fields to update")

        service_period = attrs.get("service_period")
        basic_price = attrs.get("basic_price")
        max_price = attrs.get("max_price")

        if service_period is not None and service_period < 0:
            raise serializers.ValidationError("service_period must be greater than 0")

        if basic_price is not None and basic_price < 0:
            raise serializers.ValidationError("basic_price must be greater than 0")

        if max_price is not None and max_price < 0:
            raise serializers.ValidationError("max_price must be greater than 0")

        # basic, max price 두개 들어왔는데, basic price가 max price보다 더 비싸다면 오류
        if (
            basic_price is not None
            and max_price is not None
            and basic_price > max_price
        ):
            raise serializers.ValidationError("basic_price must be less than max_price")

        return attrs

    def update(self, instance, validated_data):
        basic_price = validated_data.get("basic_price", instance.basic_price)
        max_price = validated_data.get("max_price", instance.max_price)
        if basic_price > max_price:
            raise serializers.ValidationError("basic_price must be less than max_price")

        instance.service_title = validated_data.get(
            "service_title", instance.service_title
        )
        instance.service_content = validated_data.get(
            "service_content", instance.service_content
        )
        instance.service_category = validated_data.get(
            "service_category", instance.service_category
        )
        instance.service_period = validated_data.get(
            "service_period", instance.service_period
        )
        instance.suspended = validated_data.get("suspended", instance.suspended)
        instance.save()
        return instance
