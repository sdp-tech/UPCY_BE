import uuid
from enum import unique

from django.db import models

from core.models import TimeStampedModel


def get_order_image_upload_path(instance, filename):
    service_uuid = instance.service_order.service.service_name
    order_uuid = instance.service_order.order_uuid
    return f"service/{service_uuid}/order/{order_uuid}/{filename}"


def get_order_additional_image_upload_path(instance, filename):
    service_uuid = instance.service_order.service.service_name
    order_uuid = instance.service_order.order_uuid
    additional_uuid = instance.service_order.additional_uuid
    return f"service/{service_uuid}/order/{order_uuid}/option/{additional_uuid}/{filename}"

class Order(TimeStampedModel):
    service = models.ForeignKey(
        "market.Service",
        on_delete=models.SET_NULL,
        related_name="service_order",
        null=True,
    )  # 어떤 서비스에 대한 주문인지
    request_user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="request_user_order"
    )  # 주문한 사람
    order_number = models.CharField(max_length=20, unique=True, null=False)  # 주문을 구분할 수 있는 숫자. 나중에 랜덤으로 설정될 수 있도록 수정 예정
    order_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)

    material_name = models.ManyToManyField(
        "market.ServiceMaterial",
        related_name="order_texture_name",
        blank=True,
    ) # 소재 선택
    extra_material_name = models.CharField(max_length=50, null=True)  # 기타 소재
    additional_option = models.ManyToManyField(
        "market.ServiceOption",
        related_name="additional_option_order",
        blank=True,
    ) # 옵션 선택
    additional_request = models.TextField(null=True)  # 추가 요청 사항
    order_service_price = models.PositiveIntegerField(null=True) # 서비스 금액
    order_option_price = models.PositiveIntegerField(null=True) # 옵션 추가 금액
    total_price = models.PositiveIntegerField(null=True)  # 예상 결제 금액 (서비스+옵션)
    request_date = models.DateField(null=False)  # 주문 시간
    kakaotalk_openchat_link = models.TextField(null=True)  # 카톡 오픈채팅 링크

    class Meta:
        db_table = "order"

    def save(self, *args, **kwargs):
        # Order 객체가 처음 생성될 때만 실행
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # 신규 Order일 경우 OrderState 생성
        if is_new:
            OrderState.objects.create(service_order=self)


class OrderImage(TimeStampedModel):
    # 리폼할 의류 이미지를 관리하는 테이블
    service_order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="order_image"
    )
    image = models.FileField(upload_to=get_order_image_upload_path, null=False,max_length=255)


    class Meta:
        db_table = "order_image"

class AdditionalImage(TimeStampedModel):
    #추가 요청사항 이미지를 관리하는 테이블
    service_order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="additional_image"
    )
    additional_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    image = models.FileField(upload_to=get_order_additional_image_upload_path, null=True, max_length=255) # 수정 필요

    class Meta:
        db_table = "additional_image"


class OrderState(TimeStampedModel):
    #주문 상태를 관리하는 테이블
    service_order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="order_state"
    )
    orderState_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    reformer_status = models.CharField(
        max_length=10,
        choices=[("accepted", "수락"), ("rejected", "거절"), ("pending", "대기")
            , ("received", "재료 수령"), ("produced", "제작 완료"),("deliver","배송중")
                 ,("end","거래 완료")],
        default="pending",
    )

    class Meta:
        db_table = "order_state"


class TransactionOption(TimeStampedModel):
    #거래방식 정보를 관리하는 테이블
    service_order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="transaction_option"
    )
    transaction_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    transaction_option = models.CharField(
        max_length=50, null=False, choices=[("pickup", "대면"), ("delivery", "택배")]
    )  # 거래 방식 (택배 or 대면)
    delivery_address = models.TextField(null=False)  # 결과물 배송지
    delivery_name = models.TextField(null=False) #배송 받을 이름
    delivery_phone_number= models.TextField(null=False) #배송 받을 전화번호

    class Meta:
        db_table = "transaction_option"

    def save(self, *args, **kwargs):
        # transaction_option 값이 "delivery"일 때만 DeliveryInformation 생성
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.transaction_option == "delivery":
            DeliveryInformation.objects.create(service_order=self.service_order)


class DeliveryInformation(TimeStampedModel):
    #택배 정보를 관리하는 테이블
    service_order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="delivery_information"
    )
    delivery_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    delivery_company = models.CharField(max_length=50, null=True)  # 택배 회사
    delivery_tracking_number = models.CharField(
        max_length=50, null=True
    )  # 택배 송장 번호

    class Meta:
        db_table = "delivery_information"








# 리뷰 관련된 내용은 2차 개발 기간에..