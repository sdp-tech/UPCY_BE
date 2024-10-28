from rest_framework import serializers
from order.models import TransactionOption


class TransactionOptionSerializer(serializers.ModelSerializer):
    transaction_uuid = serializers.UUIDField(read_only=True)
    class Meta:
        model = TransactionOption
        fields = [
            "transaction_uuid",
            "transaction_option",
            "delivery_address",
            "delivery_name",
            "delivery_phone_number",
        ]


    # 전화번호 유효성 검사
    def validate(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone numbers must contain only numbers.")

        return value

    def create(self, validated_data):
        transaction_option = TransactionOption.objects.create(
            service_order=self.context.get("service_order"),
            **validated_data)

        transaction_option.save()

        return transaction_option
