from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from market.pagination import ServiceListPagination
from market.services import temporary_status_check

from core.permissions import IsReformer
from market.models import Market, Service
from market.serializers.service_serializers.service_create_retrieve_serializer import (
    ServiceCreateSerializer, ServiceRetrieveSerializer)


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
                data={"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
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


class GetAllServiceView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = ServiceListPagination

    @property
    def paginator(self):
        """
        페이지네이터 인스턴스를 가져오거나 생성
        """
        if not hasattr(self, '_paginator'): # 이 객체에 paginator 멤버가 존재하지 않으면,
            if self.pagination_class is None: # pagination_class 초깃값이 정해져있지 않으면 None으로 초기화
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        쿼리셋에 페이지네이션 적용
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        페이지네이션이 적용된 응답 반환
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


    def get(self, request, **kwargs):
        try:
            service_list = Service.objects.all()
            if not service_list.exists():
                return Response(
                    data={"message": "There are no services in our database"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 페이지네이션 적용
            page = self.paginate_queryset(service_list)
            if page is not None:
                serializer = ServiceRetrieveSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            # 페이지네이션이 없는 경우 전체 데이터 반환
            serializer = ServiceRetrieveSerializer(service_list, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Service.DoesNotExist:
            return Response(
                data={"message": "There are no services in our database"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )