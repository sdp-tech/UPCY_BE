from typing import List

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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

    def get(self, request, **kwargs) -> Response:
        try:
            service = (
                Service.objects.filter(
                    market__market_uuid=kwargs.get("market_uuid"),
                    service_uuid=kwargs.get("service_uuid"),
                )
                .select_related("market")
                .first()
            )
            if not service:
                raise Service.DoesNotExist

            serializer = ServiceMaterialRetrieveSerializer(
                instance=service.service_material, many=True
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response(
                data={"message": "market service not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, **kwargs) -> Response:
        try:
            service = (
                Service.objects.filter(
                    market__market_uuid=kwargs.get("market_uuid"),
                    service_uuid=kwargs.get("service_uuid"),
                )
                .select_related("market")
                .first()
            )
            if not service:
                raise Service.DoesNotExist(
                    "해당 uuid에 해당하는 service가 존재하지 않습니다."
                )

            serializer = ServiceMaterialCreateSerializer(
                data=request.data, context={"service": service}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    data={"message": "successfully created"},
                    status=status.HTTP_201_CREATED,
                )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Service.DoesNotExist as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ServiceMaterialView(APIView):

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method in ["PUT", "DELETE"]:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs) -> Response:
        try:
            service_material: ServiceMaterial = ServiceMaterial.objects.filter(
                material_uuid=kwargs.get("material_uuid")
            ).first()
            if not service_material:
                raise ServiceMaterial.DoesNotExist

            serializer = ServiceMaterialRetrieveSerializer(instance=service_material)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except ServiceMaterial.DoesNotExist:
            return Response(
                data={"message": "service material not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs):
        try:
            serivce_material: ServiceMaterial = ServiceMaterial.objects.filter(
                material_uuid=kwargs.get("material_uuid")
            ).first()
            if not serivce_material:
                raise ServiceMaterial.DoesNotExist

            serializer = ServiceMaterialUpdateSerializer(
                instance=serivce_material, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    data={"message": "successfully updated"}, status=status.HTTP_200_OK
                )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except ServiceMaterial.DoesNotExist:
            return Response(
                data={"message": "service material not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, **kwargs):
        # service material 삭제 view
        try:
            service_material = ServiceMaterial.objects.filter(
                material_uuid=kwargs.get("material_uuid")
            ).first()
            if not service_material:
                raise ServiceMaterial.DoesNotExist

            service_material.delete()
            return Response(
                data={"message": "service material deleted"}, status=status.HTTP_200_OK
            )
        except ServiceMaterial.DoesNotExist:
            return Response(
                data={"message": "service material not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
