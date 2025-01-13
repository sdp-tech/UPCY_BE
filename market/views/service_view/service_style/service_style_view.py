from typing import List

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import view_exception_handler
from core.permissions import IsReformer
from market.models import Service, ServiceStyle
from market.serializers.service_serializers.service_style.service_style_create_serializer import (
    ServiceStyleCreateSerializer,
)
from market.serializers.service_serializers.service_style.service_style_retrieve_serializer import (
    ServiceStyleRetrieveSerializer,
)
from market.serializers.service_serializers.service_style.service_style_update_serializer import (
    ServiceStyleUpdateSerializer,
)


class ServiceStyleCreateListView(APIView):

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [IsReformer()]
        return super().get_permissions()

    @view_exception_handler
    def get(self, request, **kwargs) -> Response:
        service = (
            Service.objects.filter(
                market__market_uuid=kwargs.get("market_uuid"),
                service_uuid=kwargs.get("service_uuid"),
            )
            .select_related("market")
            .first()
        )
        if not service:
            raise ObjectDoesNotExist("market service not found")

        serializer = ServiceStyleRetrieveSerializer(
            instance=service.service_style, many=True
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @view_exception_handler
    def post(self, request, **kwargs) -> Response:
        # 1. service 객체를 service_uuid를 기준으로 데이터베이스에서 쿼리
        service: Service = (
            Service.objects.filter(service_uuid=kwargs.get("service_uuid"))
            .select_related("market")
            .first()
        )
        if not service:
            # 만약 없다면, 에러 발생 (404)
            raise ObjectDoesNotExist("Market service not found")

        # # 2. Serializer의 validate() 메서드에서 검증
        # style_name: str = request.data.get('style_name')
        # if not style_name:
        #     return Response(
        #         data={"message": "style_name is required"},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        # 3. Serializer 호출해서 처리
        serializer = ServiceStyleCreateSerializer(
            data=request.data, context={"service": service}
        )

        # 4. Serializer의 is_valid() 메서드를 호출
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={"message": "Successfully created"},
            status=status.HTTP_201_CREATED,
        )


class ServiceStyleView(APIView):
    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.method in ["PUT", "DELETE"]:
            return [IsReformer()]
        return super().get_permissions()

    @view_exception_handler
    def get(self, request, **kwargs):
        service_style = ServiceStyle.objects.filter(
            style_uuid=kwargs.get("style_uuid")
        ).first()
        if not service_style:
            raise ObjectDoesNotExist("Service style not found")

        serializer: ServiceStyleRetrieveSerializer = ServiceStyleRetrieveSerializer(
            instance=service_style
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @view_exception_handler
    def put(self, request, **kwargs) -> Response:
        service_style = ServiceStyle.objects.filter(
            style_uuid=kwargs.get("style_uuid")
        ).first()
        if not service_style:
            raise ObjectDoesNotExist("Service style not found")

        serializer = ServiceStyleUpdateSerializer(
            instance=service_style, data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data={"message": "Successfully updated"}, status=status.HTTP_200_OK
        )

    @view_exception_handler
    def delete(self, request, **kwargs) -> Response:
        service_style = ServiceStyle.objects.filter(
            style_uuid=kwargs.get("style_uuid")
        ).first()
        if not service_style:
            raise ObjectDoesNotExist("Service style not found")

        service_style.delete()
        return Response(
            data={"message": "Service style deleted"}, status=status.HTTP_200_OK
        )
