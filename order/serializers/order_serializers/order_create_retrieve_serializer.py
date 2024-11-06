from rest_framework import serializers
from order.models import (Order, OrderImage, AdditionalImage, OrderState, TransactionOption, DeliveryInformation)

class OrderImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderImage
        fields = ["image"]

class AdditionalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalImage
        fields = ["image"]

class OrderStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderState
        fields = ["orderState_uuid", "reformer_status"]

class TransactionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionOption
        fields = ["transaction_uuid",
                  "transaction_option",
                  "delivery_address",
                  "delivery_name",
                  "delivery_phone_number"]

class DeliveryInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryInformation
        fields = ["delivery_uuid",
                  "delivery_company",
                  "delivery_tracking_number"]

class OrderCreateSerializer(serializers.ModelSerializer):
    order_uuid = serializers.UUIDField(read_only=True)
    order_image = OrderImageSerializer(many=True, required=False)
    additional_image = AdditionalImageSerializer(many=True, required=False)
    order_state = OrderStateSerializer(required=True)
    transaction_option = TransactionOptionSerializer(required=False)
    delivery_information = DeliveryInformationSerializer(required=False)

    class Meta:
        model = Order
        fields = [
            "order_uuid",
            "material_name",
            "extra_material_name",
            "additional_option",
            "additional_request",
            "order_service_price",
            "order_option_price",
            "total_price",
            "request_date",
            "kakaotalk_openchat_link",
            "order_image",
            "additional_image",
            "order_state",
            "transaction_option",
            "delivery_information",
        ]

    def create(self, validated_data):
        order_images_data = validated_data.pop("order_image", [])
        additional_images_data = validated_data.pop("additional_image", [])
        order_state_data = validated_data.pop("order_state", None)
        transaction_option_data = validated_data.pop("transaction_option", None)
        delivery_information_data = validated_data.pop("delivery_information", None)

        service_order = self.context.get("service_order")
        order = Order.objects.create(service_order=service_order, **validated_data)
        order.save()


        for image_data in order_images_data:
            order_images_data = OrderImage.objects.create(order=order, **image_data)
            order_images_data.save()

        for image_data in additional_images_data:
            additional_images_data = AdditionalImage.objects.create(order=order, **image_data)
            additional_images_data.save()

        if order_state_data:
            order_state_data = OrderState.objects.create(order=order, **order_state_data)
            order_state_data.save()

        if transaction_option_data:
            transaction_option_data =TransactionOption.objects.create(order=order, **transaction_option_data)
            transaction_option_data.save()

        if delivery_information_data:
            delivery_information_data = DeliveryInformation.objects.create(order=order, **delivery_information_data)
            delivery_information_data.save()

        return order

class OrderRetrieveSerializer(serializers.ModelSerializer):
    order_uuid = serializers.UUIDField(read_only=True)
    order_image = OrderImageSerializer(many=True, required=False)
    additional_image = AdditionalImageSerializer(many=True, required=False)
    order_state = OrderStateSerializer(required=True)
    transaction_option = TransactionOptionSerializer(required=False)
    delivery_information = DeliveryInformationSerializer(required=False)

    class Meta:
        model = Order
        fields = [
            "order_uuid",
            "material_name",
            "extra_material_name",
            "additional_option",
            "additional_request",
            "order_service_price",
            "order_option_price",
            "total_price",
            "request_date",
            "kakaotalk_openchat_link",
            "order_image",
            "additional_image",
            "order_state",
            "transaction_option",
            "delivery_information",
        ]