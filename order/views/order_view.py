import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import view_exception_handler
from core.permissions import IsReformer
from market.models import Service
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

    def get_customer_orders(self) -> QuerySet:
        queryset: QuerySet = Order.objects.get_orders_by_orderer(self.request.user)
        queryset = self.apply_filters_and_sorting(queryset, self.request)

        return queryset

    def get_reformer_orders(self) -> QuerySet:
        queryset: QuerySet = Order.objects.get_orders_by_reformer(self.request.user)
        queryset = self.apply_filters_and_sorting(queryset, self.request)

        return queryset

    @view_exception_handler
    def get(self, request):
        """
        type=reformer: 본인이 처리해야 하는 모든 주문 리스트를 반환하는 API
        type=customer: 요청한 사람의 모든 주문 리스트를 반환하는 API
        """
        _type: str = request.GET.get("type")
        if not _type:
            raise ValueError("type query parameter is required")

        match _type:
            case "reformer":
                if request.user.role != "reformer":
                    raise ValueError("Only reformer can access this endpoint")
                queryset: QuerySet = self.get_reformer_orders()
            case "customer":
                queryset: QuerySet = self.get_customer_orders()
            case _:
                raise ValueError("Invalid type query parameter")

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

class ServiceOrderListView(APIView):
    permission_classes = [IsReformer]

    def get(self, request, **kwargs):
        """
        특정 서비스에 달려있는 주문 정보를 반환하는 API
        """
        service_uuid = kwargs.get("service_uuid")
        service: Service = Service.objects.filter(service_uuid=service_uuid).first()
        if not service:
            raise ObjectDoesNotExist("service not found")

        queryset: QuerySet = Order.objects.filter(service=service)
        if queryset.count() == 0:
            return Response(data=[], status=status.HTTP_204_NO_CONTENT)

        serializer = OrderRetrieveSerializer(instance=queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
