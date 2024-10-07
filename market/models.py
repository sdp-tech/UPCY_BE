import uuid
from django.db import models

from core.models import TimeStampedModel
from users.models.reformer import Reformer


def get_market_thumbnail_upload_path(instance, filename):
    email_name = instance.reformer.user.email.split("@")[0]
    market_uuid = instance.market_uuid
    return f"users/{email_name}/market/{market_uuid}/{filename}"


def get_service_image_upload_path(instance, filename):
    email_name = instance.market_service.market.reformer.user.email.split("@")[0]
    market_uuid = instance.market_service.market.market_name
    service_uuid = instance.market_service.service_uuid
    return f"users/{email_name}/market/{market_uuid}/service/{service_uuid}/{filename}"


def get_service_option_image_upload_path(instance, filename):
    email_name = instance.service_option.market_service.market.reformer.user.email.split("@")[0]
    market_uuid = instance.service_option.market_service.market.market_name
    service_uuid = instance.service_option.market_service.service_uuid
    option_uuid = instance.service_option.option_uuid
    return f"users/{email_name}/market/{market_uuid}/service/{service_uuid}/option/{option_uuid}/{filename}"


class Market(TimeStampedModel):
    reformer = models.ForeignKey(
        "users.Reformer", on_delete=models.CASCADE, related_name="market"
    )  # 리포머 한명은 여러개의 마켓을 소유할 수 있음

    market_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)  # 마켓 UUID
    market_name = models.CharField(max_length=50, null=False)  # 마켓 이름
    market_introduce = models.TextField(null=False)  # 마켓 소개
    market_address = models.CharField(max_length=50, null=False)  # 마켓 주소
    market_thumbnail = models.FileField(upload_to=get_market_thumbnail_upload_path, null=False)  # 마켓 썸네일

    class Meta:
        db_table = "market"


class Service(TimeStampedModel):
    market = models.ForeignKey(
        "market.Market", on_delete=models.CASCADE, related_name="market_service"
    )

    service_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    service_title = models.CharField(max_length=50, null=False)  # 서비스 이름
    service_content = models.TextField(null=False)  # 서비스 상세 설명
    service_category = models.CharField(max_length=50, null=False, default="None")  # 서비스 카테고리
    service_period = models.PositiveIntegerField(null=False, default=0)  # 서비스 제작 예상 기간
    basic_price = models.PositiveIntegerField(null=False, default=0)  # 서비스 기본 요금
    max_price = models.PositiveIntegerField(null=False, default=0)  # 서비스 최대 요금

    temporary = models.BooleanField(default=False) # 임시 저장 상태 변수 (프론트 요청) True인 경우, 임시 저장한 서비스라는 뜻입니다.

    class Meta:
        db_table = "market_service"


class ServiceMaterial(TimeStampedModel):
    market_service = models.ForeignKey(
        "market.Service", on_delete=models.CASCADE, related_name="service_material"
    )

    material_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    material_name = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = "market_service_material"


class ServiceStyle(TimeStampedModel):
    market_service = models.ForeignKey(
        "market.Service", on_delete=models.CASCADE, related_name="service_style"
    )

    style_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    style_name = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = "market_service_style"


class ServiceOption(TimeStampedModel):
    market_service = models.ForeignKey(
        "market.Service", on_delete=models.CASCADE, related_name="service_option"
    )

    option_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    option_name = models.CharField(max_length=50, null=False)  # 옵션 이름
    option_content = models.TextField(null=False)  # 옵션 상세 설명
    option_price = models.PositiveIntegerField(null=False)  # 옵션 요금

    class Meta:
        db_table = "market_service_option"


class ServiceImage(TimeStampedModel):
    market_service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="service_image"
    )
    image = models.FileField(upload_to=get_service_image_upload_path, null=False, max_length=255)

    class Meta:
        db_table = "market_service_image"


class ServiceOptionImage(TimeStampedModel):
    service_option = models.ForeignKey(
        ServiceOption, on_delete=models.CASCADE, related_name="service_option_image"
    )
    image = models.FileField(upload_to=get_service_option_image_upload_path, null=False, max_length=255)

    class Meta:
        db_table = "market_service_option_image"
