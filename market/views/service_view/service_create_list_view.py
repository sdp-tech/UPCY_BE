from django.db.models import QuerySet
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsReformer
from market.models import Market, Service
from market.pagination import ServiceListPagination
from market.serializers.service_serializers.service_create_retrieve_serializer import (
    ServiceCreateSerializer, ServiceRetrieveSerializer)
from market.services import temporary_status_check


class MarketServiceCreateListView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method in ["POST"]:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs):
        try:
            temporary_status = temporary_status_check(request)
            market_service = Service.objects.filter(
                market__market_uuid=kwargs.get("market_uuid"),
                temporary=temporary_status,
            ).select_related("market")
            if not market_service:
                raise Service.DoesNotExist

            serialized = ServiceRetrieveSerializer(market_service, many=True)
            return Response(data=serialized.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Service.DoesNotExist:
            return Response(
                data={"message": "There are no services in your market"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, **kwargs):
        try:
            market = Market.objects.filter(
                market_uuid=kwargs.get("market_uuid")
            ).first()
            if not market:
                raise Market.DoesNotExist
            serialized = ServiceCreateSerializer(
                data=request.data, context={"market": market}
            )
            serialized.is_valid(raise_exception=True)
            reform_service = serialized.save()
            return Response(
                data={"service_uuid": reform_service.service_uuid},
                status=status.HTTP_201_CREATED,
            )
        except Market.DoesNotExist:
            return Response(
                data={"message": "market not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetAllServiceView(ListAPIView):
    """
    데이터베이스에 존재하는 모든 서비스에 정보를 반환하는 View
    추후, 검색 기능 추가 시 이 클래스를 수정해주면 될 것 같습니다.
    기존 APIView 클래스를 상속받았던것과 달리,
    generics.ListAPIView를 활용해서 더 쉽게 API 구성이 가능합니다.
    """

    permission_classes = [AllowAny]
    serializer_class = ServiceRetrieveSerializer  # 시리얼라이저 지정
    pagination_class = ServiceListPagination  # 페이지네이션 클래스 지정

    def get_queryset(self):
        # 쿼리셋을 select_related를 사용해 최적화하여 반환
        return Service.objects.select_related("market").all()

    def get(self, request, **kwargs):
        try:
            queryset: QuerySet = self.get_queryset()
            if not queryset.exists():  # 서비스가 하나도 존재하지 않으면 404 코드 반환
                return Response(
                    data={"message": "There are no services in our database"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 페이지네이션 적용
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            # 페이지네이션이 없는 경우 전체 데이터 반환
            serializer = self.get_serializer(queryset, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
