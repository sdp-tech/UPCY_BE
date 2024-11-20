from typing import Dict, Any, List

from rest_framework import serializers
from django.db import transaction

from market.models import ServiceOption, ServiceMaterial, Service
from order.models import (
    AdditionalImage,
    DeliveryInformation,
    Order,
    OrderImage,
    OrderState,
    TransactionOption,
)
from users.models import User


class MaterialSerializer(serializers.ModelSerializer):
    material_uuid = serializers.UUIDField()

    class Meta:
        model = ServiceMaterial
        fields = ["material_uuid"]

class OptionSerializer(serializers.Serializer):
    option_uuid = serializers.UUIDField()

    class Meta:
        model = ServiceOption
        fields = ["option_uuid"]

class OrderImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderImage
        fields = ["order_image"]

class AdditionalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalImage
        fields = ["additional_image"]

class OrderStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderState
        fields = ["order_state_uuid", "reformer_status"]
        read_only_fields = ["order_state_uuid"]


class TransactionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionOption
        fields = [
            "transaction_uuid",
            "transaction_option",
            "delivery_address",
            "delivery_name",
            "delivery_phone_number",
        ]
        read_only_fields = ["transaction_uuid"]


class DeliveryInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryInformation
        fields = ["delivery_uuid", "delivery_company", "delivery_tracking_number"]
        read_only_fields = ["delivery_uuid"]


class OrderCreateSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many=True, required=True)
    additional_options = OptionSerializer(many=True, required=False)
    transaction = TransactionOptionSerializer(write_only=True, required=True)

    class Meta:
        model = Order
        fields = [
            "materials",
            "extra_material",
            "additional_request",
            "additional_options",
            "transaction",
        ]

    def validate(self, attrs):
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Order:
        service: Service = self.context['service']
        request_user: User = self.context['order_user']
        transaction_data: Dict[str, Any] | None = validated_data.pop('transaction', None)
        materials_data: List[Any] = validated_data.pop('materials', [])
        options_data: List[Any] = validated_data.pop('additional_options', [])

        with transaction.atomic():
            # 주문 생성
            order: Order = Order.objects.create(
                service_order=service,
                order_market=service.market,
                order_reformer=service.market.reformer,
                request_user=request_user,
                **validated_data
            )

            # M2M 관계 설정
            if materials_data:
                material_instances: List[Any] = []
                for material in materials_data:
                    material_instances.append(ServiceMaterial.objects.get(material_uuid=material['material_uuid']))
                order.materials.set(material_instances)

            if options_data:
                option_instances: List[Any] = []
                option_price: int = 0
                for option in options_data:
                    option_instance: ServiceOption = ServiceOption.objects.get(option_uuid=option['option_uuid'])
                    option_instances.append(option_instance)
                    option_price += option_instance.option_price
                order.additional_options.set(option_instances)

            # 추가 금액 및 카카오톡 링크 업데이트
            order.order_service_price = order.service_order.basic_price
            order.order_option_price = option_price
            order.total_price = order.order_service_price + order.order_option_price
            order.kakaotalk_openchat_link = service.market.reformer.reformer_link
            order.save()

            # 거래 옵션 생성
            if transaction_data:
                service_transaction: TransactionOption = TransactionOption.objects.create(
                    service_order=order,
                    **transaction_data
                )
                if service_transaction.transaction_option == "delivery":
                    DeliveryInformation.objects.create(
                        service_order = order
                    ) # 나머지는 PUT 요청을 통해 택배 정보 업데이트

            # 주문 상태 생성
            OrderState.objects.create(
                service_order=order,
                reformer_status="pending"
            )

            return order


class OrderRetrieveSerializer(serializers.ModelSerializer):
    order_uuid = serializers.UUIDField(read_only=True)
    order_image = OrderImageSerializer(many=True, required=False)
    additional_image = AdditionalImageSerializer(many=True, required=False)
    order_state = OrderStateSerializer(required=True)
    transaction_option = TransactionOptionSerializer(required=False)
    delivery_information = DeliveryInformationSerializer(required=False)

    extra_material_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    additional_request = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )  # 추가 요청 사항
    order_service_price = serializers.IntegerField(
        required=False, allow_null=True
    )  # 서비스 금액
    order_option_price = serializers.IntegerField(
        required=False, allow_null=True
    )  # 옵션 추가 금액
    total_price = serializers.IntegerField(
        required=False, allow_null=True
    )  # 예상 결제 금액 (서비스 + 옵션)
    request_date = serializers.DateField(required=True)  # 주문 날짜
    kakaotalk_openchat_link = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )  # 카톡 오픈채팅 링크

    class Meta:
        model = Order
