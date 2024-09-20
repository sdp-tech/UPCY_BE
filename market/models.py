import uuid

from django.db import models

from core.models import TimeStampedModel

def get_market_thumbnail_upload_path(instance, filename):
    user_id = instance.reformer.user.id
    market_name = instance.market_name
    return f"users/{user_id}/market/{market_name}/thumbnail/{filename}"

def get_service_image_upload_path(instance, filename):
    user_id = instance.market_service.market.reformer.user.id
    market_name = instance.market_service.market.market_name
    service_title = instance.market_service.service_title
    return f"users/{user_id}/market/{market_name}/service/{service_title}/image/{filename}"

class Market(TimeStampedModel):
    # 리포머의 마켓 정보
    reformer = models.ForeignKey('users.Reformer', on_delete=models.CASCADE, related_name='market') # 리포머 한명은 여러개의 마켓을 소유할 수 있음

    market_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4) # 마켓 UUID
    market_name = models.CharField(max_length=50, null=False) # 마켓 이름
    market_introduce = models.TextField(null=False) # 마켓 소개
    market_address = models.CharField(max_length=50, null=False) # 마켓 주소
    market_thumbnail = models.FileField(upload_to=get_market_thumbnail_upload_path, null=False) # 마켓 썸네일
    # market_rate = models.DecimalField(max_digits=2, decimal_places=1, default=0.0) # 마켓 평점 -> 추후 리뷰기능 개발 시 추가

    class Meta:
        db_table = 'market'

class MarketService(TimeStampedModel):
    # 리포머의 마켓에서 제공하는 서비스에 대한 모델
    market = models.ForeignKey('market.Market', on_delete=models.CASCADE, related_name='market_service')

    service_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    service_title = models.CharField(max_length=50, null=False) # 서비스 이름
    service_content = models.TextField(null=False) # 서비스 상세 설명
    service_category = models.CharField(max_length=50, null=False) # 서비스 카테고리
    service_period = models.CharField(max_length=50, null=False) # 서비스 제작 예상 기간
    basic_price = models.IntegerField(null=False) # 서비스 기본 요금
    max_price = models.IntegerField(null=False) # 서비스 최대 요금
    # service_request_count = models.IntegerField(null=False, default=0) # 서비스 이용 수 -> 추후 개발

    class Meta:
        db_table = 'market_service'

class ServiceMaterial(TimeStampedModel):
    # 해당 서비스에서 사용하는 재료 ( 작업 가능한 소재 )
    market_service = models.ForeignKey('market.MarketService', on_delete=models.CASCADE, related_name='service_material')

    material_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    material_name = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = 'market_service_material'

class ServiceStyle(TimeStampedModel):
    # 해당 서비스가 제공하는 스타일
    market_service = models.ForeignKey('market.MarketService', on_delete=models.CASCADE, related_name='service_style')

    style_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    style_name = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = 'market_service_style'

class ServiceOption(TimeStampedModel):
    # 서비스 작성 시 추가하는 옵션에 대한 테이블
    market_service = models.ForeignKey('market.MarketService', on_delete=models.CASCADE, related_name='service_option')

    option_uuid = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    option_name = models.CharField(max_length=50, null=False) # 옵션 이름
    option_content = models.TextField(null=False) # 옵션 상세 설명
    option_price = models.IntegerField(null=False) # 옵션 요금

    class Meta:
        db_table = 'market_service_option'

class ServiceImage(TimeStampedModel):
    # 서비스 소개 이미지 관리 테이블
    market_service = models.ForeignKey('market.MarketService', on_delete=models.CASCADE, related_name='service_image')
    image = models.FileField(upload_to=get_service_image_upload_path, null=False)

    class Meta:
        db_table = 'market_service_image'
