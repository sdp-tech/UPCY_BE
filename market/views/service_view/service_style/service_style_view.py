from typing import List
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from core.permissions import IsReformer
from market.models import Service, ServiceStyle
from market.serializers.service_serializers.service_style.service_style_create_serializer import \
    ServiceStyleCreateSerializer
from market.serializers.service_serializers.service_style.service_style_retrieve_serializer import \
    ServiceStyleRetrieveSerializer
from market.serializers.service_serializers.service_style.service_style_update_serializer import \
    ServiceStyleUpdateSerializer


class ServiceStyleCreateListView(APIView):
    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs) -> Response:
        try:
            service = Service.objects.filter(
                market__market_uuid=kwargs.get('market_uuid'),
                service_uuid=kwargs.get('service_uuid')
            ).select_related('market').first()
            if not service:
                return Response(
                    data={"message": "Market service not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = ServiceStyleRetrieveSerializer(
                instance=service.service_style, many=True
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except Service.DoesNotExist:
            return Response(
                data={"message": "Service not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"message": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, **kwargs) -> Response:
        try:
            # 1. service 객체를 service_uuid를 기준으로 데이터베이스에서 쿼리
            service: Service = Service.objects.filter(
                service_uuid=kwargs.get('service_uuid')
            ).select_related('market').first()
            if not service:
                # 만약 없다면, 에러 발생 (404)
                raise Service.DoesNotExist("Market service not found")

            # # 2. Serializer의 validate() 메서드에서 검증
            # style_name: str = request.data.get('style_name')
            # if not style_name:
            #     return Response(
            #         data={"message": "style_name is required"},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )

            # 3. Serializer 호출해서 처리
            serializer = ServiceStyleCreateSerializer(
                data=request.data,
                context={"service": service}
            )

            # 4. Serializer의 is_valid() 메서드를 호출
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    data={"message": "Successfully created"},
                    status=status.HTTP_201_CREATED
                )
        except Service.DoesNotExist as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"message": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ServiceStyleView(APIView):
    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method in ["PUT", "DELETE"]:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs):
        try:
            service_style = ServiceStyle.objects.filter(
                style_uuid=kwargs.get("style_uuid")
            ).first()
            if not service_style:
                raise ServiceStyle.DoesNotExist("Service style not found")

            serializer: ServiceStyleRetrieveSerializer = ServiceStyleRetrieveSerializer(instance=service_style)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except ServiceStyle.DoesNotExist as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs) -> Response:
        try:
            service_style = ServiceStyle.objects.filter(
                style_uuid=kwargs.get('style_uuid')
            ).first()
            if not service_style:
                return Response(
                    data={"message": "Service style not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = ServiceStyleUpdateSerializer(
                instance=service_style, data=request.data
            )

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    data={"message": "Successfully updated"},
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                data={"message": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, **kwargs) -> Response:
        try:
            service_style = ServiceStyle.objects.filter(
                style_uuid=kwargs.get('style_uuid')
            ).first()
            if not service_style:
                return Response(
                    data={"message": "Service style not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            service_style.delete()
            return Response(
                data={"message": "Service style deleted"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                data={"message": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
