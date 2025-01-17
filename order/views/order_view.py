import logging

from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import view_exception_handler
from order.mixins import OrderQueryParamMinxin
from order.models import Order
from order.pagination import OrderListPagination
from order.serializers.order_create_serializer import (
    OrderCreateResponseSerializer,
    OrderCreateSerializer,
)
from order.serializers.order_retrieve_serializer import OrderRetrieveSerializer

logger = logging.getLogger(__name__)


class OrderView(OrderQueryParamMinxin, APIView):
    permission_classes = [IsAuthenticated]
    paginator = OrderListPagination()

    def get_queryset(self) -> QuerySet:
        queryset: QuerySet = Order.objects.get_orders_by_orderer(self.request.user)
        queryset = self.apply_filters_and_sorting(queryset, self.request)

        return queryset

    @view_exception_handler
    def get(self, request):
        queryset: QuerySet = self.get_queryset()

        paginated_queryset = self.paginator.paginate_queryset(queryset, request)
        serializer: OrderRetrieveSerializer = OrderRetrieveSerializer(
            instance=paginated_queryset, many=True
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @view_exception_handler
    def post(self, request):
        logger.debug("POST : /api/orders")
        logger.debug(request.data)

        serializer: OrderCreateSerializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        logger.debug("serializer 검증 완료 -> save() 호출")
        order: Order = serializer.save()  # create 호출

        response_serializer: OrderCreateResponseSerializer = (
            OrderCreateResponseSerializer(instance=order)
        )  # 응답 생성

        return Response(data=response_serializer.data, status=status.HTTP_201_CREATED)
