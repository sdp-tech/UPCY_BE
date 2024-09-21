from django.db import models

from core.models import TimeStampedModel


class Order(TimeStampedModel):
    service = models.ForeignKey('market.Service', on_delete=models.SET_NULL, related_name='service_order', null=True) # 어떤 서비스에 대한 주문인지?
    request_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='request_user_order') # 주문한 사람
    request_detail = models.TextField(null=False) # 기본 요구 사항
    delivery_address = models.TextField(null=False) # 결과물 배송지
    size = models.CharField(max_length=50, null=False) # 리폼 의류 사이즈
    additional_option = models.ForeignKey('market.ServiceOption', on_delete=models.SET_NULL, related_name='additional_option_order', null=True)
    total_price = models.IntegerField(null=False) # 최종 리폼 견적 금액
    request_date = models.DateField(null=False) # 주문 시간
    due_date = models.DateField(null=False) # 마감 시간
    transaction_option = models.CharField(max_length=50, null=False, choices=[('pickup', '대면'), ('delivery', '택배')]) # 거래 방식 (택배 or 대면)
    request_canceled = models.BooleanField(default=False) # 주문 취소 여부
    portfolio_status = models.BooleanField(default=False) # 해당 주문 포트폴리오 사용 가능 여부
    additional_request = models.TextField(null=True) # 추가 요청 사항
    payment_status = models.BooleanField(default=False) # 입금 여부
    material_received_status = models.BooleanField(default=False) # 주문자가 발송한 재료를 리포머가 수령했는지에 대한 여부
    delivery_company = models.CharField(max_length=50, null=True) # 택배 회사
    delivery_tracking_number = models.CharField(max_length=50, null=True) # 택배 송장 번호
    kakaotalk_openchat_link = models.TextField(null=True) # 카톡 오픈채팅 링크

    class Meta:
        db_table = 'order'

class OrderImage(TimeStampedModel):
    # 리폼 요구사항 작성 시 첨부하는 이미지를 관리하는 테이블
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name='order_image')
    image = models.FileField(upload_to='order_image') # 수정 필요

    class Meta:
        db_table = 'order_image'

class OrderCategory(TimeStampedModel):
    # 리폼 요구사항 카테고리 정보를 저장하는 테이블
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name='order_category')
    category = models.CharField(max_length=50, null=False) # 주문 카테고리

    class Meta:
        db_table = 'order_category'

class OrderReformStyle(TimeStampedModel):
    # 리폼 스타일 정보를 저장하는 테이블
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name='order_style')
    style_name = models.CharField(max_length=50, null=False) # 스타일 이름

    class Meta:
        db_table = 'order_reform_style'

class OrderReformTexture(TimeStampedModel):
    # 리폼할 의류의 재료 정보? 재질 정보? 를 저장하는 테이블
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name='order_texture')
    texture_name = models.CharField(max_length=50, null=False) # 재질 이름

    class Meta:
        db_table = 'order_reform_texture'

class OrderReformFit(TimeStampedModel):
    # 리폼할 의류의 핏 정보를 저장하는 테이블
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name='order_fit')
    fit_name = models.CharField(max_length=50, null=False) # 핏 이름

    class Meta:
        db_table = 'order_reform_fit'

# 리뷰 관련된 내용은 2차 개발 기간에..
