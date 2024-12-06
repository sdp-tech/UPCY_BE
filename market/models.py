import uuid

from django.db import models

from core.models import TimeStampedModel
from market.managers import MarketManager, ServiceManager, ServiceMaterialManager
from users.models.reformer import Reformer


def get_market_thumbnail_upload_path(instance, filename):
    email_name = instance.reformer.user.email.split("@")[0]
    market_uuid = instance.market_uuid
    return f"users/{email_name}/market/{market_uuid}/{filename}"


def get_service_image_upload_path(instance, filename):
    email_name = instance.market_service.market.reformer.user.email.split("@")[
        0
    ]  # market을 통해 reformer에 접근
    market_uuid = instance.market_service.market.market_name
    service_uuid = instance.market_service.service_uuid
    return f"users/{email_name}/market/{market_uuid}/service/{service_uuid}/{filename}"


def get_service_option_image_upload_path(instance, filename):
    email_name = (
        instance.service_option.market_service.market.reformer.user.email.split("@")[0]
    )  # market을 통해 reformer에 접근
    market_uuid = instance.service_option.market_service.market.market_name
    service_uuid = instance.service_option.market_service.service_uuid
    option_uuid = instance.service_option.option_uuid
    return f"users/{email_name}/market/{market_uuid}/service/{service_uuid}/option/{option_uuid}/{filename}"


class Market(TimeStampedModel):
    # 리포머의 마켓 정보
    reformer = models.ForeignKey(
        "users.Reformer", on_delete=models.CASCADE, related_name="market"
    )  # 리포머 한명은 여러개의 마켓을 소유할 수 있음

    market_uuid = models.UUIDField(
        null=False, unique=True, default=uuid.uuid4
    )  # 마켓 UUID
    market_name = models.CharField(max_length=50, null=False)  # 마켓 이름
    market_introduce = models.TextField(null=False)  # 마켓 소개
    market_address = models.CharField(max_length=50, null=False)  # 마켓 주소
    market_thumbnail = models.FileField(
        upload_to=get_market_thumbnail_upload_path, null=False
    )  # 마켓 썸네일
    # market_rate = models.DecimalField(max_digits=2, decimal_places=1, default=0.0) # 마켓 평점 -> 추후 리뷰기능 개발 시 추가

    objects = MarketManager()

    class Meta:
        db_table = "market"


class Service(TimeStampedModel):
    # 리포머의 마켓에서 제공하는 서비스에 대한 모델
    market = models.ForeignKey(
        "market.Market", on_delete=models.CASCADE, related_name="market_service"
    )

    service_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    service_title = models.CharField(max_length=50, null=False)  # 서비스 이름
    service_content = models.TextField(null=False)  # 서비스 상세 설명
    service_category = models.CharField(
        max_length=50, null=False, default="None"
    )  # 서비스 카테고리
    service_period = models.PositiveIntegerField(
        null=False, default=0
    )  # 서비스 제작 예상 기간
    basic_price = models.PositiveIntegerField(null=False, default=0)  # 서비스 기본 요금
    max_price = models.PositiveIntegerField(null=False, default=0)  # 서비스 최대 요금
    suspended = models.BooleanField(
        null=False, default=False
    )  # 서비스가 일시 중단되었는지 확인하는 필드
    temporary = models.BooleanField(
        default=False
    )  # 해당 서비스가 임시 저장된 상태인지 표시하는 필드. True인 경우, 임시 저장된 데이터이다.

    objects = ServiceManager()

    class Meta:
        db_table = "market_service"


class ServiceMaterial(TimeStampedModel):
    # 해당 서비스에서 사용하는 재료 ( 작업 가능한 소재 )
    market_service = models.ForeignKey(
        "market.Service", on_delete=models.CASCADE, related_name="service_material"
    )

    material_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    material_name = models.CharField(max_length=50, null=False)

    objects = ServiceMaterialManager()

    class Meta:
        db_table = "market_service_material"


class ServiceStyle(TimeStampedModel):
    # 해당 서비스가 제공하는 스타일
    market_service = models.ForeignKey(
        "market.Service", on_delete=models.CASCADE, related_name="service_style"
    )

    style_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    style_name = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = "market_service_style"


class ServiceOption(TimeStampedModel):
    # 서비스 작성 시 추가하는 옵션에 대한 테이블
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
    # 서비스 소개 이미지 관리 테이블
    market_service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="service_image"
    )
    image = models.FileField(
        upload_to=get_service_image_upload_path, null=False, max_length=255
    )

    class Meta:
        db_table = "market_service_image"


class ServiceOptionImage(TimeStampedModel):
    # 서비스 옵션 이미지 관리 테이블
    service_option = models.ForeignKey(
        ServiceOption,
        on_delete=models.CASCADE,
        related_name="service_option_image",
    )
    image = models.FileField(
        upload_to=get_service_option_image_upload_path, null=False, max_length=255
    )

    class Meta:
        db_table = "market_service_option_image"
