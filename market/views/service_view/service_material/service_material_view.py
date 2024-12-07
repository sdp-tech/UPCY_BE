from typing import List

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import view_exception_handler
from core.permissions import IsReformer
from market.models import Service, ServiceMaterial
from market.serializers.service_serializers.service_material.service_material_create_serializer import (
    ServiceMaterialCreateSerializer,
)
from market.serializers.service_serializers.service_material.service_material_retrieve_serializer import (
    ServiceMaterialRetrieveSerializer,
)
from market.serializers.service_serializers.service_material.service_material_update_serializer import (
    ServiceMaterialUpdateSerializer,
)


class ServiceMaterialCreateListView(APIView):

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.method in ["POST"]:
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

        serializer = ServiceMaterialRetrieveSerializer(
            instance=service.service_material, many=True
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @view_exception_handler
    def post(self, request, **kwargs) -> Response:
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

        serializer = ServiceMaterialCreateSerializer(
            data=request.data, context={"service": service}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={"message": "successfully created"},
            status=status.HTTP_201_CREATED,
        )


class ServiceMaterialView(APIView):

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.method in ["PUT", "DELETE"]:
            return [IsReformer()]
        return super().get_permissions()

    @view_exception_handler
    def get(self, request, **kwargs) -> Response:
        service_material: ServiceMaterial = (
            ServiceMaterial.objects.get_service_material_by_material_uuid(
                material_uuid=kwargs.get("material_uuid")
            )
        )
        serializer = ServiceMaterialRetrieveSerializer(instance=service_material)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @view_exception_handler
    def put(self, request, **kwargs) -> Response:
        service_material: ServiceMaterial = (
            ServiceMaterial.objects.get_service_material_by_material_uuid(
                material_uuid=kwargs.get("material_uuid")
            )
        )
        serializer: ServiceMaterialUpdateSerializer = ServiceMaterialUpdateSerializer(
            instance=service_material, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={"message": "successfully updated"}, status=status.HTTP_200_OK
        )

    @view_exception_handler
    def delete(self, request, **kwargs):
        # service material 삭제 view
        service_material: ServiceMaterial = (
            ServiceMaterial.objects.get_service_material_by_material_uuid(
                material_uuid=kwargs.get("material_uuid")
            )
        )

        service_material.delete()
        return Response(
            data={"message": "service material deleted"}, status=status.HTTP_200_OK
        )
