import os

from boto3 import client
from django.db import transaction
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsReformer
from order.models import Order
from order.pagination import OrderListPagination
from order.serializers.order_serializers.order_create_retrieve_serializer import (
    OrderRetrieveSerializer,
)
from order.serializers.order_serializers.order_update_serializer import (
    OrderUpdateSerializer,
)


class ReformerOrderListView(APIView):
    def get_permissions(self):
        if self.request.method == ["GET", "PUT"]:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs) -> Response:
        try:
            order_uuid = kwargs.get("order_uuid")
            order = (
                Order.objects.filter(order_uuid=order_uuid, request_user=request.user)
                .select_related("request_user")
                .first()
            )
            if not order:
                raise Order.DoesNotExist

            serialized = OrderRetrieveSerializer(instance=order, many=True)
            return Response(data=serialized.data, status=status.HTTP_200_OK)
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
                .select_related("request_user")
                .first()
            )
            serialized = OrderUpdateSerializer(instance=order)
            serialized.is_valid(raise_exception=True)
            serialized.save()
            return Response(data=serialized.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                data={"message": "order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
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


class GetReformerAllOrderView(ListAPIView):

    permission_classes = [IsReformer]
    serializer_class = OrderRetrieveSerializer
    pagination_class = OrderListPagination

    def get_queryset(self):
        return (
            Order.objects.filter(order_reformer=self.request.user.reformer)
            .select_related("request_user", "service", "service__market")
            .all()
        )

    def get(self, request, **kwargs):
        try:
            queryset: QuerySet = self.get_queryset()
            if not queryset.exists():
                return Response(
                    data={"message": "There are no orders in our database"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )