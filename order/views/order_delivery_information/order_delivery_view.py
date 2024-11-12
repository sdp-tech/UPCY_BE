from typing import List

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsReformer
from order.models import DeliveryInformation, Order
<<<<<<< HEAD
from order.serializers.order_serializers.order_delivery_information.order_delivery_create_serializer import \
    DeliveryInformationCreateSerializer
from order.serializers.order_serializers.order_delivery_information.order_delivery_retrieve_serializer import \
    DeliveryInformationRetrieveSerializer
from order.serializers.order_serializers.order_delivery_information.order_delivery_update_serializer import \
    DeliveryInformationUpdateSerializer
=======
from order.serializers.order_serializers.order_delivery_information.order_delivery_create_serializer import (
    DeliveryInformationCreateSerializer,
)
from order.serializers.order_serializers.order_delivery_information.order_delivery_retrieve_serializer import (
    DeliveryInformationRetrieveSerializer,
)
from order.serializers.order_serializers.order_delivery_information.order_delivery_update_serializer import (
    DeliveryInformationUpdateSerializer,
)

>>>>>>> c58c23774c09e48cfe239ed971af9fe92c340c29


class OrderDeliveryCreateView(APIView):
    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method == "POST":
            return [IsReformer()]

    def get(self, request, **kwargs) -> Response:
        try:
            order = (
                Order.objects.filter(
                    service_uuid=kwargs.get("service_uuid"),
                    order_uuid=kwargs.get("order_uuid"),
                )
                .select_related("service")
                .first()
            )
            if not order:
                raise Order.DoesNotExist

            serializer = DeliveryInformationRetrieveSerializer(
                instance=order.delivery_information
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                data={"message": "Order not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, **kwargs) -> Response:
        try:
            order = (
                Order.objects.filter(
                    service_uuid=kwargs.get("service_uuid"),
                    order_uuid=kwargs.get("order_uuid"),
                )
                .select_related("service")
                .first()
            )
            if not order:
                raise Order.DoesNotExist

            serializer = DeliveryInformationCreateSerializer(
                data=request.data, context={"service_order": order}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    data={"message": "successfully created"},
                    status=status.HTTP_201_CREATED,
                )
        except Order.DoesNotExist:
            return Response(
                data={"message": "service order not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderDeliveryView(APIView):
    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method == "PUT":
            return [IsReformer()]

    def get(self, request, **kwargs) -> Response:
        try:
            delivery_information: DeliveryInformation = (
                DeliveryInformation.objects.filter(
                    delivery_uuid=kwargs.get("delivery_uuid")
                ).first()
            )
            if not delivery_information:
                raise DeliveryInformation.DoesNotExist

            serializer = DeliveryInformationRetrieveSerializer(
                instance=delivery_information
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except DeliveryInformation.DoesNotExist:
            return Response(
                data={"message": "delivery information not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs) -> Response:
        try:
            delivery_information: DeliveryInformation = (
                DeliveryInformation.objects.filter(
                    delivery_uuid=kwargs.get("delivery_uuid")
                ).first()
            )
            if not delivery_information:
                raise DeliveryInformation.DoesNotExist

            serializer = DeliveryInformationUpdateSerializer(
                instance=delivery_information, data=request.data
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
        except DeliveryInformation.DoesNotExist:
            return Response(
                data={"message": "delivery information not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
