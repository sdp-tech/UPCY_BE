import logging
from typing import Optional

from django.db import transaction
from rest_framework import serializers

from market.models import Service, ServiceMaterial, ServiceOption
from order.models import (
    DeliveryInformation,
    Order,
    OrdererInformation,
    OrderImage,
    OrderStatus,
    Transaction,
)
from users.serializers.user_serializer.user_information_serializer import (
    UserInformationSerializer,
)

logger = logging.getLogger(__name__)


class OrderImageSerializer(serializers.ModelSerializer):
    image_uuid = serializers.UUIDField(read_only=True)
    image_type = serializers.CharField(read_only=True)

    class Meta:
        model = OrderImage
        fields = [
            "image_uuid",
            "image_type",
            "image",
        ]
        extra_kwargs = {
            "image": {"required": False},
        }


class OrderCreateSerializer(serializers.ModelSerializer):
    order_uuid = serializers.UUIDField(read_only=True)
    transaction_option = serializers.CharField()
    service_uuid = serializers.UUIDField(write_only=True)
    materials = serializers.ListField(write_only=True)
    options = serializers.ListField(write_only=True)
    orderer_name = serializers.CharField(write_only=True, required=False)
    orderer_phone_number = serializers.CharField(write_only=True, required=False)
    orderer_email = serializers.EmailField(write_only=True, required=False)
    orderer_address = serializers.CharField(write_only=True, required=False)
    images = serializers.ListField(child=serializers.ImageField())
    orderer = UserInformationSerializer(read_only=True)
    service_price = serializers.IntegerField()
    option_price = serializers.IntegerField()
    total_price = serializers.IntegerField()

    class Meta:
        model = Order
        fields = [
            "orderer",
            "order_uuid",
            "transaction_option",
            "extra_material",
            "additional_request",
            "service_price",
            "option_price",
            "total_price",
            "images",
            "materials",
            "options",
            "service_uuid",
            "orderer_name",
            "orderer_phone_number",
            "orderer_email",
            "orderer_address",
        ]
        extra_kwargs = {
            "orderer_name": {"required": False},
            "orderer_phone_number": {"required": False},
            "orderer_email": {"required": False},
            "orderer_address": {"required": False},
            "transaction_option": {"required": True},
            "extra_material": {"required": False},
            "additional_request": {"required": False},
            "service_price": {"required": True},
            "option_price": {"required": True},
            "total_price": {"required": True},
            "order_date": {"required": False},
            "images": {"required": False},
        }

    def validate(self, attrs):
        if (
            "option_price" in attrs
            and attrs.get("option_price") is not None
            and attrs.get("option_price") < 0
        ):
            raise serializers.ValidationError("Option price must be greater than 0")

        if (
            "service_price" in attrs
            and attrs.get("service_price") is not None
            and attrs.get("service_price") < 0
        ):
            raise serializers.ValidationError("Service price must be greater than 0")

        service_price = attrs.get("service_price")
        option_price = attrs.get("option_price")
        total_price = attrs.get("total_price")

        if service_price + option_price != total_price:
            raise serializers.ValidationError(
                "Service price + Option price must be equal to total price"
            )

        return attrs

    @transaction.atomic()
    def create(self, validated_data) -> Order:
        logger.debug(f"1. OrderSerializer.create() 호출됨: {validated_data}")

        # multipart data에서 images 따로 빼기
        images = validated_data.pop("images", [])
        logger.debug(f"2. multipart data에서 images 따로 빼기 : {images}")

        # 주문자 정보가 주어졌다면 -> validated_data에서 빼기
        # 주문자 정보가 주어지지 않았다면 -> request.user로 찾으면 됨
        # 주문 조회할 때 Order 테이블과 연결된 OrdererInformation 테이블이 존재한다면, 해당 테이블을 쓰고
        # 주문 조회할 때 Order 테이블과 연결된 OrdererInformation 테이블이 존재하지 않아면, User 테이블에서 가져오면 된다.
        orderer_fields = [
            "orderer_name",
            "orderer_phone_number",
            "orderer_email",
            "orderer_address",
        ]
        orderer_data = {}
        for field in orderer_fields:
            # pop으로 뽑아와서 None / 빈 문자열인 경우도 체크
            value = validated_data.pop(field, None)
            if value:  # 값이 있다면 orderer_data에 저장
                orderer_data[field] = value

        logger.debug(f"3. orderer_data : {orderer_data}")

        materials: list = validated_data.pop("materials", [])
        logger.debug(f"materials : {materials}")
        options: list = validated_data.pop("options", [])
        logger.debug(f"options : {options}")

        # materials, options로 넘어온 UUID에 대한 ServiceMaterial, ServiceOption 객체 가져오기
        material_instances = ServiceMaterial.objects.filter(
            material_uuid__in=materials
        )  # in을 사용해서 리스트 안에 들어있는 모든 값에 대한 UUID에 해당하는 객체를 가져올 수 있음
        option_instances = ServiceOption.objects.filter(option_uuid__in=options)
        logger.debug(f"4. material_instances : {material_instances.count()}")
        logger.debug(f"5. option_instances : {option_instances.count()}")

        # Transaction option 추출
        transaction_option: str = validated_data.pop("transaction_option")
        logger.debug(f"6. transaction_option : {transaction_option}")

        # 서비스UUID 사용해서 서비스 객체 찾아오기
        service_uuid: Optional[str] = validated_data.pop("service_uuid", None)
        if not service_uuid:
            raise serializers.ValidationError("service_uuid is required")
        service: Service = Service.objects.filter(service_uuid=service_uuid).first()
        validated_data["service"] = service

        # 주문 생성
        validated_data["orderer"] = self.context["request"].user
        order: Order = Order.objects.create(**validated_data)
        logger.debug(f"7. Order 생성 성공")

        # 주문자 정보 생성 (만약 따로 orderer 정보가 들어왔다면)
        if orderer_data:
            logger.debug("7-1. There is orderer data")
            OrdererInformation.objects.create(
                user=self.context.get("request").user, order=order, **orderer_data
            )
            logger.debug(f"7-2. OrdererInformation 생성 성공")

        order.materials.set(material_instances)
        order.additional_options.set(option_instances)
        order.save()
        logger.debug(f"8. order : {order}")

        # 이미지 저장 인스턴스 생성
        if images:
            queryset: list[OrderImage] = [
                OrderImage(order=order, image=image) for image in images
            ]
            OrderImage.objects.bulk_create(queryset)
        logger.debug(f"9. OrderImage에 이미지 저장 성공")
        logger.debug(f"OrderImage 개수 : {len(OrderImage.objects.all())}")

        order_status: OrderStatus = OrderStatus.objects.create(order=order)
        logger.debug(f"10. OrderStatus 생성 성공")

        trans: Transaction = Transaction.objects.create(
            order=order, transaction_option=transaction_option
        )
        if trans.transaction_option == "delivery":
            # DeliveryInformation에 들어가는 정보는 추후 Reformer가 업데이트 해야함
            # 여기서는 단순히 인스턴스만 생성
            DeliveryInformation.objects.create(transaction=transaction)
        logger.debug(f"11. TransactionOption 생성 성공")

        return order


class OrderCreateResponseSerializer(serializers.ModelSerializer):
    order_status = serializers.SerializerMethodField()

    def get_order_status(self, obj):
        return obj.order_status.order_by("created").first().status

    class Meta:
        model = Order
        fields = ["order_uuid", "order_status", "order_date"]
