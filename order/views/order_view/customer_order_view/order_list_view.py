from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsCustomer
from market.models import Service
from order.models import Order
from order.pagination import OrderListPagination
from order.serializers.order_serializers.order_create_retrieve_serializer import (
    OrderCreateSerializer,
    OrderRetrieveSerializer,
)


class CustomerOrderCreateListView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request, **kwargs) -> Response:
        try:
            order_uuid = kwargs.get("order_uuid")
            order = (
                Order.objects.filter(order_uuid=order_uuid, request_user=request.user)
                .select_related("request_user", "service")
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

    def post(self, request, **kwargs) -> Response:
        """
        주문 생성 요청(POST) 처리 함수
        """
        try:
            service_uuid = kwargs.get("service_uuid")
            if not service_uuid:
                return Response(
                    data={"message": "service uuid is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            service = Service.objects.filter(service_uuid=service_uuid).first()
            if not service:
                raise Service.DoesNotExist(
                    "service_uuid에 해당하는 서비스가 존재하지 않습니다."
                )

            serializer = OrderCreateSerializer(
                data=request.data,
                context={"order_user": request.user, "service": service},
            )
            serializer.is_valid(raise_exception=True)
            created_order: Order = serializer.save()

            return Response(
                data={"order_uuid": created_order.order_uuid},
                status=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except ObjectDoesNotExist as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetCustomerAllOrderView(ListAPIView):

    permission_classes = [AllowAny]
    serializer_class = OrderRetrieveSerializer
    pagination_class = OrderListPagination

    def get_queryset(self):
        return Order.objects.select_related("request_user").all()

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
