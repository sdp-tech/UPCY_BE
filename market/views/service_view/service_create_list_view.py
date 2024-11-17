from botocore.exceptions import ValidationError
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
    ServiceCreateSerializer,
    ServiceRetrieveSerializer,
)
from market.services import temporary_status_check


class MarketServiceCreateListView(APIView):
    """
    market uuid를 사용하여
    서비스 생성 또는 전체 서비스 리스트를 가져오는 view
    """

    # 쿼리 파라미터로 전달 가능 한 필드 지정
    DEFAULT_SORT = "-created"
    ALLOWED_SORT_FIELDS = {
        "created": "created",  # 생성 된 날짜 기준 오름차순
        "-created": "-created",  # 생성 된 날짜 기준 내림차순 (가장 최근에 생성된 서비스 항목)
        "updated": "updated",  # 업데이트 된 서비스 오름차순
        "-updated": "-updated",  # 업데이트 된 서비스 내림차순 (가장 최근에 업데이트 된 서비스 항목)
        "title": "service_title",  # 서비스 제목 오름차순
        "-title": "-service_title",  # 서비스 제목 내림차순
        "category": "service_category",  # 카테고리 이름 오름차순
        "-category": "-service_category",  # 카테고리 이름 내림차순
        "basic_price": "basic_price",  # 기본 가격 오름차순
        "-basic_price": "-basic_price",  # 기본 가격 내림차순
    }

    def get_queryset(self, market_uuid: str, temporary: bool) -> QuerySet:
        """
        쿼리셋 반환 및 정렬 적용
        """
        queryset = Service.objects.filter(
            market__market_uuid=market_uuid, temporary=temporary
        ).select_related("market")
        if not queryset.exists():
            raise Service.DoesNotExist("해당 마켓에 생성된 서비스가 존재하지 않습니다.")

        sort_param = self.request.GET.get("sort")
        if sort_param:
            if sort_param in self.ALLOWED_SORT_FIELDS:
                queryset = queryset.order_by(self.ALLOWED_SORT_FIELDS[sort_param])
            else:
                raise ValueError("정렬 파라미터 값이 올바르지 않습니다.")
        else:
            queryset = queryset.order_by(
                self.ALLOWED_SORT_FIELDS[self.DEFAULT_SORT]
            )  # 따로 안넘어왔다면 기본값으로 created 내림차순 정렬

        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.method in ["POST"]:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs):
        try:
            temporary_status = temporary_status_check(request)
            queryset = self.get_queryset(
                market_uuid=kwargs.get("market_uuid"), temporary=temporary_status
            )

            serialized = ServiceRetrieveSerializer(queryset, many=True)
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

            serializer = ServiceCreateSerializer(
                data=request.data, context={"market": market}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                data=serializer.data,
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

    # 쿼리 파라미터로 전달 가능 한 필드 지정
    DEFAULT_SORT = "-created"
    ALLOWED_SORT_FIELDS = {
        "created": "created",  # 생성 된 날짜 기준 오름차순
        "-created": "-created",  # 생성 된 날짜 기준 내림차순 (가장 최근에 생성된 서비스 항목)
        "updated": "updated",  # 업데이트 된 서비스 오름차순
        "-updated": "-updated",  # 업데이트 된 서비스 내림차순 (가장 최근에 업데이트 된 서비스 항목)
        "title": "service_title",  # 서비스 제목 오름차순
        "-title": "-service_title",  # 서비스 제목 내림차순
        "category": "service_category",  # 카테고리 이름 오름차순
        "-category": "-service_category",  # 카테고리 이름 내림차순
        "basic_price": "basic_price",  # 기본 가격 오름차순
        "-basic_price": "-basic_price",  # 기본 가격 내림차순
    }

    def get_queryset(self) -> QuerySet:
        """
        쿼리셋 반환 및 정렬 적용
        """
        queryset = Service.objects.select_related("market").all()

        sort_param = self.request.GET.get("sort")
        if sort_param:
            if sort_param in self.ALLOWED_SORT_FIELDS:
                queryset = queryset.order_by(self.ALLOWED_SORT_FIELDS[sort_param])
            else:
                raise ValueError("정렬 파라미터 값이 올바르지 않습니다.")
        else:
            queryset = queryset.order_by(
                self.ALLOWED_SORT_FIELDS[self.DEFAULT_SORT]
            )  # 따로 안넘어왔다면 기본값으로 created 내림차순 정렬

        return queryset

    def list(self, request, **kwargs) -> Response:
        try:
            queryset: QuerySet = self.get_queryset()
            if not queryset.exists():  # 서비스가 하나도 존재하지 않으면 404 코드 반환
                return Response(
                    data={"message": "데이터베이스에 서비스 인스턴스가 하나도 없어요"},
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
        except ValueError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
