from typing import List

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsReformer
from order.models import Order, OrderState
from order.serializers.order_serializers.order_state.order_state_create_serializer import \
    OrderStateCreateSerializer
from order.serializers.order_serializers.order_state.order_state_retrieve_serializer import \
    OrderStateRetrieveSerializer
from order.serializers.order_serializers.order_state.order_state_update_serializer import \
    OrderStateUpdateSerializer


class OrderStateCreateView(APIView):
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

            serializer = OrderStateRetrieveSerializer(instance=order.OrderState)
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

            serializer = OrderStateCreateSerializer(
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


class OrderStateView(APIView):
    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method == "PUT":
            return [IsReformer()]

    def get(self, request, **kwargs) -> Response:
        try:
            order_state: OrderState = OrderState.objects.filter(
                order_state_uuid=kwargs.get("order_state_uuid")
            ).first()
            if not order_state:
                raise OrderState.DoesNotExist

            serializer = OrderStateRetrieveSerializer(instance=order_state)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except OrderState.DoesNotExist:
            return Response(
                data={"message": "order state not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs) -> Response:
        try:
            order_state: OrderState = OrderState.objects.filter(
                order_state_uuid=kwargs.get("order_state_uuid")
            ).first()
            if not order_state:
                raise OrderState.DoesNotExist

            serializer = OrderStateUpdateSerializer(
                instance=order_state, data=request.data
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
        except OrderState.DoesNotExist:
            return Response(
                data={"message": "order state not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
