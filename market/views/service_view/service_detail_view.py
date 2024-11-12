import os

from boto3 import client
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsReformer
from market.models import Service, ServiceImage
from market.serializers.service_serializers.service_create_retrieve_serializer import \
    ServiceRetrieveSerializer
from market.serializers.service_serializers.service_update_serializer import \
    ServiceUpdateSerializer
from market.services import temporary_status_check


class MarketServiceCrudView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method in ["POST", "PUT", "DELETE"]:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs) -> Response:
        try:
            temporary_status = temporary_status_check(request)
            market_service = (
                Service.objects.filter(
                    market__market_uuid=kwargs.get("market_uuid"),
                    service_uuid=kwargs.get("service_uuid"),
                    temporary=temporary_status,
                )
                .select_related("market")
                .first()
            )
            if not market_service:
                raise Service.DoesNotExist(
                    "해당 조건과 UUID에 해당하는 서비스가 존재하지 않습니다."
                )

            serializer = ServiceRetrieveSerializer(instance=market_service)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Service.DoesNotExist as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs):
        try:
            market_service = (
                Service.objects.filter(
                    market__market_uuid=kwargs.get("market_uuid"),
                    service_uuid=kwargs.get("service_uuid"),
                )
                .select_related("market")
                .first()
            )
            if not market_service:
                raise Service.DoesNotExist

            serializer = ServiceUpdateSerializer(
                instance=market_service, data=request.data
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    data={"message": "market service updated"},
                    status=status.HTTP_200_OK,
                )
        except (ValidationError, KeyError) as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
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

    def delete(self, request, **kwargs):
        try:
            market_service = (
                Service.objects.filter(
                    market__market_uuid=kwargs.get("market_uuid"),
                    service_uuid=kwargs.get("service_uuid"),
                )
                .select_related("market")
                .first()
            )
            if not market_service:
                raise Service.DoesNotExist

            market_service_images = ServiceImage.objects.filter(
                market_service=market_service
            )
            with transaction.atomic():
                s3 = client("s3")
                if market_service_images:
                    s3.delete_objects(
                        Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                        Delete={
                            "Objects": [
                                {"Key": service_image.image.name}
                                for service_image in market_service_images
                            ]
                        },
                    )
                market_service.delete()
            return Response(
                data={"message": "market service deleted"}, status=status.HTTP_200_OK
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
