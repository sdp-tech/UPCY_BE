import uuid

from django.db import models

from core.models import TimeStampedModel
from order.managers import OrderManager, OrderStatusManager


def get_order_image_upload_path(instance, filename):
    return f"orders/{instance.order.order_uuid}/{instance.image_type}/{filename}"


class _OrderStatus(models.TextChoices):
    ACCEPTED = "accepted", "수락"
    REJECTED = "rejected", "거절"
    PENDING = "pending", "대기"
    RECEIVED = "received", "재료 수령"
    PRODUCED = "produced", "제작 완료"
    DELIVER = "deliver", "배송중"
    END = "end", "거래 완료"


class Order(TimeStampedModel):
    service = models.ForeignKey(
        "market.Service",
        on_delete=models.SET_NULL,
        related_name="service_order",
        null=True,
        db_index=True,  # service 가지고 reformer, market까지 다 찾아야하니까 인덱스 설정
    )  # 어떤 서비스에 대한 주문인지

    orderer = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="orderer"
    )  # 주문한 사람

    order_uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )  # 주문 번호

    materials = models.ManyToManyField(
        "market.ServiceMaterial",
        related_name="materials_order",
        blank=True,
    )  # 사용 소재
    extra_material = models.CharField(
        max_length=50, null=True
    )  # 기타 소재 -> Text로 입력
    additional_options = models.ManyToManyField(
        "market.ServiceOption",
        related_name="additional_options_order",
        blank=True,
    )  # 옵션 선택

    additional_request = models.TextField(null=True)  # 추가 요청 사항
    service_price = models.PositiveIntegerField(null=True)  # 서비스 금액
    option_price = models.PositiveIntegerField(null=True)  # 옵션 추가 금액
    total_price = models.PositiveIntegerField(null=True)  # 저장된 필드로 변경
    rejected_reason = models.TextField(null=True)  # 거절 사유
    order_date = models.DateField(auto_now_add=True)  # 주문 시간

    objects = OrderManager()

    def save(self, *args, **kwargs):
        self.total_price = (self.service_price or 0) + (self.option_price or 0)
        super().save(*args, **kwargs)

    class Meta:
        db_table = "order"


class OrdererInformation(TimeStampedModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="user_order_information"
    )
    order = models.OneToOneField(
        "order.Order", on_delete=models.CASCADE, related_name="orderer_information"
    )

    orderer_name = models.CharField(max_length=50, null=False)
    orderer_phone_number = models.CharField(max_length=50, null=False)
    orderer_email = models.EmailField(max_length=254, null=True)
    orderer_address = models.TextField(null=False)

    class Meta:
        db_table = "orderer"


class OrderStatus(TimeStampedModel):
    # 주문 상태를 관리하는 테이블
    order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="order_status"
    )
    status = models.CharField(
        max_length=10,
        choices=_OrderStatus.choices,
        default="pending",
    )

    objects = OrderStatusManager()

    class Meta:
        db_table = "order_status"


class OrderImage(TimeStampedModel):
    order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="order_image"
    )
    image_type = models.CharField(
        max_length=20,
        choices=[("order", "order"), ("additional", "additional")],
        default="order",
    )
    image_uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    image = models.FileField(upload_to=get_order_image_upload_path)


class Transaction(TimeStampedModel):
    # 거래방식 정보를 관리하는 테이블
    order = models.OneToOneField(
        "order.Order", on_delete=models.CASCADE, related_name="transaction"
    )
    transaction_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    transaction_option = models.CharField(
        max_length=50, null=False, choices=[("pickup", "대면"), ("delivery", "택배")]
    )  # 거래 방식 (택배 or 대면)

    class Meta:
        db_table = "transaction"


class DeliveryInformation(TimeStampedModel):
    # 택배 정보를 관리하는 테이블
    # 주문 정보 생성 시 transaction_option이 delivery인 경우, DeliveryInformation 새로 생성
    transaction = models.ForeignKey(
        "order.Transaction",
        on_delete=models.CASCADE,
        related_name="delivery_information",
    )
    delivery_company = models.CharField(max_length=50, null=True)  # 택배 회사
    delivery_tracking_number = models.CharField(
        max_length=50, null=True
    )  # 택배 송장 번호
    delivery_address = models.TextField(
        null=True, blank=True, default=None
    )  # 결과물 배송지
    delivery_name = models.TextField(
        null=True, blank=True, default=None
    )  # 배송 받을 이름
    delivery_phone_number = models.TextField(
        null=True, blank=True, default=None
    )  # 배송 받을 전화번호

    class Meta:
        db_table = "delivery_information"
