from django.db import transaction
from market.models import ServiceImage, Service, Market
from django.core.exceptions import ValidationError

class MarketImageUploadService:
    def __init__(self):
        pass

    @staticmethod
    @transaction.atomic
    def upload_market_image(market: Market, image_file) -> None:
        """
        마켓 썸네일 이미지를 S3에 업로드 및 데이터베이스에 저장하는 함수
        """
        try:
            if image_file.size > 10 * 1024 * 1024:  # 10MB 이상의 프로필 이미지는 안됨!
                raise ValidationError("Image file size must be less than 10MB")

            if market.market_thumbnail: # 마켓 썸네일 이미지는 딱 하나이므로, 기존 이미지 먼저 삭제
                market.market_thumbnail.delete()

            market.market_thumbnail = image_file
            market.save()
            print("Successfully uploaded market thumbnail image")  # 추후 로그 출력으로 수정!!!
        except ValidationError as e:
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise e

    @staticmethod
    @transaction.atomic
    def upload_service_image(market_service: Service, image_file) -> None:
        """
        서비스 소개 이미지를 S3에 업로드 및 데이터베이스에 저장하는 함수
        """
        try:
            if image_file.size > 10 * 1024 * 1024:  # 10MB 이상의 프로필 이미지는 안됨!
                raise ValidationError("Image file size must be less than 10MB")

            service_image = ServiceImage.objects.create(
                market_service=market_service,
                image=image_file
            )
            service_image.save()
            print("Successfully uploaded service image") # 추후 로그 출력으로 수정!!!
        except ValidationError as e:
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise e

    @staticmethod
    @transaction.atomic
    def upload_service_option_image(market_service: Service, image_file) -> None:
        """
        서비스 소개 이미지를 S3에 업로드 및 데이터베이스에 저장하는 함수
        """
        try:
            if image_file.size > 10 * 1024 * 1024:  # 10MB 이상의 프로필 이미지는 안됨!
                raise ValidationError("Image file size must be less than 10MB")

            service_image = ServiceImage.objects.create(
                market_service=market_service,
                image=image_file
            )
            service_image.save()
            print("Successfully uploaded service option image")  # 추후 로그 출력으로 수정!!!
        except ValidationError as e:
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise e