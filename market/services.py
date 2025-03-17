import os
from typing import Any, List

from boto3 import client
from django.core.exceptions import ValidationError
from django.db import transaction

from market.models import (
    Market,
    Service,
    ServiceImage,
    ServiceOption,
    ServiceOptionImage,
)


def validate_image_files(image_files: List) -> None:
    """이미지 파일의 유효성을 검사하는 함수"""
    for image_file in image_files:
        if image_file.size > 10 * 1024 * 1024:  # 10MB 이상의 이미지는 허용되지 않음
            raise ValidationError("Image file size must be less than 10MB")


def temporary_status_check(request) -> bool:
    # 쿼리 파라미터로 temporary 변수를 문자열로 받아옴
    temporary_status = request.GET.get("temporary", "false").lower()

    # 'true' 또는 'false'만을 허용하고, bool 값으로 변환
    if temporary_status == "true":
        temporary_status = True
    elif temporary_status == "false":
        temporary_status = False
    else:
        raise ValueError("temporary는 true와 false값만 사용할 수 있습니다")

    return temporary_status


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
                        Key=market.market_thumbnail.name,
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
    def upload_service_images(entity: Any, image_files) -> None:
        """
        서비스 소개 이미지를 S3에 업로드 및 데이터베이스에 저장하는 함수
        """
        try:
            # 파일 유효성 검증
            validate_image_files(image_files)

            if isinstance(entity, Service):
                bulk_images: List[ServiceImage] = []
                for image_file in image_files:
                    bulk_images.append(
                        ServiceImage(market_service=entity, image=image_file)
                    )
                ServiceImage.objects.bulk_create(bulk_images)

        except ValidationError as e:
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise e

    @staticmethod
    @transaction.atomic
    def upload_service_option_images(entity: Any, image_files) -> None:
        """
        서비스 옵션 이미지를 S3에 업로드 및 데이터베이스에 저장하는 함수
        """
        try:
            # 파일 유효성 검증
            validate_image_files(image_files)

            # 엔티티 타입 별 쿼리 생성
            if isinstance(entity, ServiceOption):
                bulk_images: List[ServiceOptionImage] = []
                for image_file in image_files:
                    bulk_images.append(
                        ServiceOptionImage(service_option=entity, image=image_file)
                    )
                ServiceOptionImage.objects.bulk_create(bulk_images)

        except ValidationError as e:
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise e
