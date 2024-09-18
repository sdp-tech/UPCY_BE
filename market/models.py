from django.db import models

from core.models import TimeStampedModel


class Market(TimeStampedModel):
    # 리포머의 마켓 정보
    reformer = models.ForeignKey('users.ReformerProfile', on_delete=models.CASCADE, related_name='market')
    market_name = models.CharField(max_length=50, null=False) # 마켓 이름
    market_introduce = models.TextField(null=False) # 마켓 소개
    market_address = models.CharField(max_length=50, null=False) # 마켓 주소
    market_thumbnail = models.FileField(upload_to='market_thumbnail', null=False) # 수정 필요
    market_rate = models.DecimalField(max_digits=2, decimal_places=1) # 마켓 평점

    class Meta:
        db_table = 'market'

class MarketService(TimeStampedModel):
    # 리포머의 마켓에서 제공하는 서비스에 대한 모델
    reformer = models.ForeignKey('users.ReformerProfile', on_delete=models.CASCADE, related_name='reformer_service')
    market = models.ForeignKey('market.Market', on_delete=models.CASCADE, related_name='market_service')
    service_title = models.CharField(max_length=50, null=False) # 서비스 이름
    service_content = models.TextField(null=False) # 서비스 상세 설명
    service_category = models.CharField(max_length=50, null=False) # 서비스 카테고리
    service_style = models.CharField(max_length=50, null=False) # 해당 서비스의 스타일
    service_period = models.CharField(max_length=50, null=False) # 서비스 제작 예상 기간
    basic_price = models.IntegerField(null=False) # 서비스 기본 요금
    max_price = models.IntegerField(null=False) # 서비스 최대 요금
    service_request_count = models.IntegerField(null=False) # 서비스 이용 수

    class Meta:
        db_table = 'market_service'

class ServiceOption(TimeStampedModel):
    # 서비스 작성 시 추가하는 옵션에 대한 테이블
    market_service = models.ForeignKey('market.MarketService', on_delete=models.CASCADE, related_name='service_option')
    option_name = models.CharField(max_length=50, null=False) # 옵션 이름
    option_content = models.TextField(null=False) # 옵션 상세 설명
    option_price = models.IntegerField(null=False) # 옵션 요금

    class Meta:
        db_table = 'service_option'