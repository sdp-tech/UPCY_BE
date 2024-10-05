from django.db import models

from core.models import TimeStampedModel


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
    additional_option = models.ForeignKey(
        "market.ServiceOption",
        on_delete=models.SET_NULL,
        related_name="additional_option_order",
        null=True,
    )
    additional_request = models.TextField(null=True)  # 추가 요청 사항
    total_price = models.IntegerField(null=False)  # 최종 리폼 견적 금액
    request_date = models.DateField(null=False)  # 주문 시간
    kakaotalk_openchat_link = models.TextField(null=True)  # 카톡 오픈채팅 링크

    class Meta:
        db_table = "order"


class OrderImage(TimeStampedModel):
    # 리폼할 의류 이미지를 관리하는 테이블
    order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="order_image"
    )
    image = models.FileField(upload_to="order_image")  # 수정 필요

    class Meta:
        db_table = "order_image"

class AdditionalImage(TimeStampedModel):
    #추가 요청사항 이미지를 관리하는 테이블
    order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="additional_image"
    )
    image = models.FileField(upload_to="additional_image") # 수정 필요

    class Meta:
        db_table = "additional_image"


class OrderState(TimeStampedModel):
    #주문 상태를 관리하는 테이블
    order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="order_state"
    )
    reformer_status = models.CharField(
        max_length=10,
        choices=[("accepted", "수락"), ("rejected", "거절"), ("pending", "대기")
            , ("received", "재료 수령"), ("produced", "제작완료"),("deliver","배송중")
                 ,("end","거래 완료")],
        default="pending",
    )

    class Meta:
        db_table = "order_state"


class TransactionOption(TimeStampedModel):
    #거래방식 정보를 관리하는 테이블
    order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="transaction_option"
    )
    transaction_option = models.CharField(
        max_length=50, null=False, choices=[("pickup", "대면"), ("delivery", "택배")]
    )  # 거래 방식 (택배 or 대면)
    delivery_address = models.TextField(null=False)  # 결과물 배송지
    delivery_name = models.TextField(null=False) #배송 받을 이름
    delivery_phone_number= models.TextField(null=False) #배송 받을 전화번호

    class Meta:
        db_table = "transaction_option"


class DeliveryInformation(TimeStampedModel):
    #택배 정보를 관리하는 테이블
    order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="delivery_information"
    )
    delivery_company = models.CharField(max_length=50, null=True)  # 택배 회사
    delivery_tracking_number = models.CharField(
        max_length=50, null=True
    )  # 택배 송장 번호

    class Meta:
        db_table = "delivery_information"



class OptionCategory(TimeStampedModel):
    # 옵션 카테고리 정보를 저장하는 테이블
    order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="option_category"
    )
    option_category = models.CharField(max_length=50, null=False)  # 옵션 카테고리

    class Meta:
        db_table = "option_category"


class OrderReformTexture(TimeStampedModel):
    # 리폼할 의류의 재질정보를 저장하는 테이블
    order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="order_texture"
    )
    texture_name = models.CharField(max_length=50, null=False)  # 재질 이름

    class Meta:
        db_table = "order_reform_texture"



# 리뷰 관련된 내용은 2차 개발 기간에..