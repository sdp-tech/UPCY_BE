import os
from typing import Any, List

from boto3 import client
from django.core.exceptions import ValidationError
from django.db import transaction

from market.models import Service
from order.models import (Order, OrderImage, AdditionalImage)

def validate_image_files(image_files: List) -> None:
    """이미지 파일의 유효성을 검사하는 함수"""
    for image_file in image_files:
        if image_file.size > 10 * 1024 * 1024:  # 10MB 이상의 이미지는 허용되지 않음
            raise ValidationError("Image file size must be less than 10MB")



class OrderImageUploadService :
    def __init__(self):
        pass

    @staticmethod
    @transaction.atomic
    def upload_order_images(entity: Any, image_files: List) -> None:
        """
        리폼할 의류 및 추가 요청사항 이미지(단일 및다중 파일)를 S3에 업로드
        & DB에 저장하는 함수
        """
        try:
            #단일 파일인 경우 리스트로 변환하여 처리
            if not isinstance(image_files, list):
                image_files = [image_files]

            images = []

            #파일 유효성 검증
            validate_image_files(image_files)

            # 엔티티 타입 별 쿼리 생성
            if isinstance(entity, Order):
                for image_file in image_files:
                    images.append(OrderImage(service_order=entity, image=image_file))
                # OrderImage > Bulk create 수행
                OrderImage.objects.bulk_create(images)

            elif isinstance(entity, AdditionalImage):
                for image_file in image_files:
                    images.append(AdditionalImage(service_order=entity, image=image_file))
                # AdditionalImage > Bulk create
                AdditionalImage.objects.bulk_create(images)


        except ValidationError as e:
            raise ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise e



