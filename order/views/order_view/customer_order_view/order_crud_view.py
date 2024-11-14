import os

from boto3 import client
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsCustomer
from order.models import Order
from order.serializers.order_serializers.order_create_retrieve_serializer import (
    OrderCreateSerializer,
)
from order.serializers.order_serializers.order_update_serializer import (
    OrderUpdateSerializer,
)


class OrderCrudView(APIView):
    def get_permissions(self):
        if self.request.method == ["GET", "POST", "PUT", "DELETE"]:
            return [IsCustomer()]
        return super().get_permissions()

    def get(self, request, **kwargs) -> Response:
        try:
            order_uuid = kwargs.get("order_uuid")
            order = (
                Order.objects.filter(order_uuid=order_uuid, request_user=request.user)
            ).first()  # request 보낸 customer의 order만 볼 수 있음
            if not order:
                raise Order.DoesNotExist

            serialized = OrderCreateSerializer(instance=order, many=True)
            serialized.is_valid(raise_exception=True)
            return Response(serialized.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                data={"message": "order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs) -> Response:
        try:
            order_uuid = kwargs.get("order_uuid")
            order = (
                Order.objects.filter(order_uuid=order_uuid, request_user=request.user)
                .select_related("request_user_order")
                .first()
            )
            if not order:
                raise Order.DoesNotExist

            serialized = OrderUpdateSerializer(instance=order, data=request.data)
            if serialized.is_valid(raise_exception=True):
                serialized.save()
                return Response(
                    data={"message": "order updated"}, status=status.HTTP_200_OK
                )
        except Order.DoesNotExist:
            return Response(
                data={"message": "order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, **kwargs):
        try:
            order = (
                Order.objects.filter(
                    order_uuid=kwargs.get("order_uuid"), request_user=request.user
                )
                .select_related("request_user_order")
                .first()
            )
            if not order:
                raise Order.DoesNotExist

            with transaction.atomic():
                s3 = client("s3")
                s3.delete_object(
                    Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                    Key=order.order_image.name,
                )
                order.delete()
                return Response(
                    data={"message": "order deleted"}, status=status.HTTP_204_NO_CONTENT
                )
        except Order.DoesNotExist:
            return Response(
                data={"message": "order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
