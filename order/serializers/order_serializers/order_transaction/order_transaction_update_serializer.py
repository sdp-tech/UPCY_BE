from rest_framework import serializers

from order.models import TransactionOption


class TransactionOptionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionOption
        fields = [
            "transaction_option",
            "delivery_address",
            "delivery_name",
            "delivery_phone_number",
        ]

    # 전화번호 유효성 검사 및 대면 비대면 여부에 따른 추가 정보 제한
    def validate(self, value):
        if value.get("transaction_option") == "pickup":
            value["delivery_address"] = ""
            value["delivery_name"] = ""
            value["delivery_phone_number"] = ""
        if not value.get("delivery_phone_number").isdigit():
            raise serializers.ValidationError(
                "Phone numbers must contain only numbers."
            )
        return value

    # 기존 TransactionOption 객체 업데이트
    def update(self, instance, validated_data):
        instance.transaction_option = validated_data.get(
            "transaction_option", instance.transaction_option
        )
        instance.delivery_address = validated_data.get(
            "delivery_address", instance.delivery_address
        )
        instance.delivery_name = validated_data.get(
            "delivery_name", instance.delivery_name
        )
        instance.delivery_phone_number = validated_data.get(
            "delivery_phone_number", instance.delivery_phone_number
        )

        instance.save()
        return instance