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

    # 여기 all 써야하는지 first 써야하는지 모르겠음

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
