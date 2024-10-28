from rest_framework import serializers
from order.models import Order


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "material_name",
            "extra_material_name",
            "additional_option",
            "additional_request",
            "order_service_price",
            "order_option_price",
            "total_price",
            "request_date",
            "kakaotalk_openchat_link",
        ]
        extra_kwargs = {
            "material_name": {"required": False},
            "extra_material_name": {"required": False},
            "additional_option": {"required": False},
            "additional_request": {"required": False},
            "order_service_price": {"required": False},
            "order_option_price": {"required": False},
            "total_price": {"required": False},
            "request_date": {"required": False},
            "kakaotalk_openchat_link": {"required": False},
        }


    def update(self, instance, validated_data):
        instance.material_name.set(validated_data.get("material_name", instance.material_name.all()))
        instance.extra_material_name = validated_data.get("extra_material_name", instance.extra_material_name)
        instance.additional_option.set(validated_data.get("additional_option", instance.additional_option.all()))
        instance.additional_request = validated_data.get("additional_request", instance.additional_request)

        order_service_price = validated_data.get("order_service_price", instance.order_service_price)
        order_option_price = validated_data.get("order_option_price", instance.order_option_price)
        total_price = validated_data.get("total_price", instance.total_price)

        instance.order_service_price = order_service_price
        instance.order_option_price = order_option_price
        instance.total_price = total_price
        instance.request_date = validated_data.get("request_date", instance.request_date)
        instance.kakaotalk_openchat_link = validated_data.get("kakaotalk_openchat_link",
                                                              instance.kakaotalk_openchat_link)

        instance.save()
        return instance