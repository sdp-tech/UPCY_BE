from typing import Any, List

from django.core.exceptions import ValidationError
from django.db import transaction

from market.models import (Market, Service, ServiceImage, ServiceOption,
                           ServiceOptionImage)

from boto3 import client
import os


def validate_image_files(image_files: List) -> None:
    """이미지 파일의 유효성을 검사하는 함수"""
    for image_file in image_files:
        if image_file.size > 10 * 1024 * 1024:  # 10MB 이상의 이미지는 허용되지 않음
            raise ValidationError("Image file size must be less than 10MB")


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
            validate_image_files([image_file])

            # 마켓 썸네일 이미지는 딱 하나이므로, 기존 이미지 먼저 삭제
            with transaction.atomic():
                if market.market_thumbnail:
                    s3 = client("s3")
                    s3.delete_object(
                        Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                        Key=market.market_thumbnail.name
                    )
                    market.market_thumbnail.delete()

                market.market_thumbnail = image_file
                market.save()
        except ValidationError as e:
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise e

    @staticmethod
    @transaction.atomic
    def upload_service_images(entity: Any, image_files: List) -> None:
        """
        서비스 소개 이미지를 S3에 업로드 및 데이터베이스에 저장하는 함수
        """
        try:
            images = []

            # 파일 유효성 검증
            validate_image_files(image_files)

            # 엔티티 타입 별 쿼리 생성
            for image_file in image_files:
                if isinstance(entity, Service):
                    images.append(ServiceImage(market_service=entity, image=image_file))
                elif isinstance(entity, ServiceOption):
                    images.append(
                        ServiceOptionImage(service_option=entity, image=image_file)
                    )

            # Bulk create
            if images and isinstance(entity, Service):
                ServiceImage.objects.bulk_create(images)
            elif images and isinstance(entity, ServiceOption):
                ServiceOptionImage.objects.bulk_create(images)

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
                market_service=market_service, image=image_file
            )
            service_image.save()
            print(
                "Successfully uploaded service option image"
            )  # 추후 로그 출력으로 수정!!!
        except ValidationError as e:
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise e
