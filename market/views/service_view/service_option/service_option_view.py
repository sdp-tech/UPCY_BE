import os
from typing import List

from boto3 import client
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsReformer
from market.models import Service, ServiceOption, ServiceOptionImage
from market.serializers.service_serializers.service_option.service_option_create_serializer import (
    ServiceOptionCreateSerializer,
)
from market.serializers.service_serializers.service_option.service_option_retrieve_serializer import (
    ServiceOptionRetrieveSerializer,
)
from market.serializers.service_serializers.service_option.service_option_update_serializer import (
    ServiceOptionUpdateSerializer,
)


class ServiceOptionCreateListView(APIView):

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.method in ["POST"]:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs) -> Response:
        try:
            service = (
                Service.objects.filter(
                    market__market_uuid=kwargs.get("market_uuid"),
                    service_uuid=kwargs.get("service_uuid"),
                )
                .select_related("market")
                .first()
            )
            if not service:
                raise Service.DoesNotExist

            serializer = ServiceOptionRetrieveSerializer(
                instance=service.service_option, many=True
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response(
                data={"message": "market service not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, **kwargs) -> Response:
        try:
            service = (
                Service.objects.filter(
                    market__market_uuid=kwargs.get("market_uuid"),
                    service_uuid=kwargs.get("service_uuid"),
                )
                .select_related("market")
                .first()
            )
            if not service:
                raise Service.DoesNotExist

            serializer = ServiceOptionCreateSerializer(
                data=request.data, context={"service": service}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    data={"message": "successfully created"},
                    status=status.HTTP_201_CREATED,
                )
        except Service.DoesNotExist:
            return Response(
                data={"message": "market service not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ServiceOptionView(APIView):

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.method in ["PUT", "DELETE"]:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs) -> Response:
        try:
            service_option: ServiceOption = ServiceOption.objects.filter(
                option_uuid=kwargs.get("option_uuid")
            ).first()
            if not service_option:
                raise ServiceOption.DoesNotExist

            serializer = ServiceOptionRetrieveSerializer(instance=service_option)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except ServiceOption.DoesNotExist:
            return Response(
                data={"message": "service option not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs) -> Response:
        try:
            service_option: ServiceOption = ServiceOption.objects.filter(
                option_uuid=kwargs.get("option_uuid")
            ).first()
            if not service_option:
                raise ServiceOption.DoesNotExist

            serializer = ServiceOptionUpdateSerializer(
                instance=service_option, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    data={"message": "successfully updated"}, status=status.HTTP_200_OK
                )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except ServiceOption.DoesNotExist:
            return Response(
                data={"message": "service option not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, **kwargs) -> Response:
        # service option 삭제 view
        try:
            service_option = ServiceOption.objects.filter(
                option_uuid=kwargs.get("option_uuid")
            ).first()
            if not service_option:
                raise ServiceOption.DoesNotExist

            with transaction.atomic():
                s3 = client("s3")
                service_option_images = ServiceOptionImage.objects.filter(
                    service_option=service_option
                )

                s3.delete_objects(
                    Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                    Delete={
                        "Objects": [
                            {"Key": service_option_image.image.name}
                            for service_option_image in service_option_images
                        ]
                    },
                )
                service_option_images.delete()  # 연관된 이미지 먼저 삭제
                service_option.delete()  # Service option 삭제

            return Response(
                data={"message": "service option deleted"}, status=status.HTTP_200_OK
            )
        except ServiceOption.DoesNotExist:
            return Response(
                data={"message": "service option not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
