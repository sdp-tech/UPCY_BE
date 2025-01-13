from django.db.models import QuerySet
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import view_exception_handler
from core.permissions import IsReformer
from market.mixins import ServiceQueryParamMixin
from market.models import Market, Service
from market.pagination import ServiceListPagination
from market.serializers.service_serializers.service_create_retrieve_serializer import (
    ServiceCreateSerializer,
    ServiceRetrieveSerializer,
)
from market.services import temporary_status_check
from users.serializers.reformer_serializer.reformer_profile_serializer import (
    ReformerProfileSerializer,
)


class MarketServiceCreateListView(ServiceQueryParamMixin, APIView):
    """
    market uuid를 사용하여
    서비스 생성 또는 전체 서비스 리스트를 가져오는 view
    """

    def get_queryset(self, market_uuid: str, temporary: bool) -> QuerySet:
        """
        쿼리셋 반환 및 정렬 적용
        """
        queryset = Service.objects.get_service_queryset_by_market_uuid_with_temporary(
            market_uuid=market_uuid, temporary=temporary
        )
        queryset = self.apply_filters_and_sorting(queryset, self.request)

        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.method in ["POST"]:
            return [IsReformer()]
        return super().get_permissions()

    @view_exception_handler
    def get(self, request, **kwargs):
        """
        마켓에 생성된 서비스 리스트를 반환하는 로직을 처리하는 View
        """
        temporary_status = temporary_status_check(request)
        queryset = self.get_queryset(
            market_uuid=kwargs.get("market_uuid"), temporary=temporary_status
        )

        serialized = ServiceRetrieveSerializer(queryset, many=True)
        return Response(data=serialized.data, status=status.HTTP_200_OK)

    @view_exception_handler
    def post(self, request, **kwargs):
        """
        서비스 생성 메서드
        """
        market: Market = Market.objects.get_market_by_market_uuid(
            market_uuid=kwargs.get("market_uuid")
        )

        serializer = ServiceCreateSerializer(
            data=request.data, context={"market": market}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )


class GetAllServiceView(ServiceQueryParamMixin, ListAPIView):
    """
    데이터베이스에 존재하는 모든 서비스에 정보를 반환하는 View
    추후, 검색 기능 추가 시 이 클래스를 수정해주면 될 것 같습니다.
    기존 APIView 클래스를 상속받았던것과 달리,
    generics.ListAPIView를 활용해서 더 쉽게 API 구성이 가능합니다.
    """

    permission_classes = [AllowAny]
    serializer_class = ServiceRetrieveSerializer  # 시리얼라이저 지정
    pagination_class = ServiceListPagination  # 페이지네이션 클래스 지정

    def get_queryset(self) -> QuerySet:
        """
        쿼리셋 반환 및 정렬 적용
        """
        queryset: QuerySet = Service.objects.get_all_service_queryset()
        queryset = self.apply_filters_and_sorting(queryset, self.request)

        return queryset

    @view_exception_handler
    def list(self, request, **kwargs) -> Response:
        queryset: QuerySet = self.get_queryset()

        # 페이지네이션 적용
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # 페이지네이션이 없는 경우 전체 데이터 반환
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
