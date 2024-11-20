from typing import List

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsCustomer
from order.models import Order, TransactionOption
from order.serializers.order_serializers.order_transaction.order_transaction_create_serializer import (
    TransactionOptionCreateSerializer,
)
from order.serializers.order_serializers.order_transaction.order_transaction_retrieve_serializer import (
    TransactionOptionRetrieveSerializer,
)
from order.serializers.order_serializers.order_transaction.order_transaction_update_serializer import (
    TransactionOptionUpdateSerializer,
)


class OrderTransactionOptionCreateView(APIView):

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method == "POST":
            return [IsCustomer()]

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

            serializer = TransactionOptionRetrieveSerializer(
                instance=order.transaction_option
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

            serializer = TransactionOptionCreateSerializer(
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


class OrderTransactionOptionView(APIView):

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method == "PUT":
            return [IsCustomer()]

    def get(self, request, **kwargs) -> Response:
        try:
            transaction_option: TransactionOption = TransactionOption.objects.filter(
                transaction_uuid=kwargs.get("transaction_uuid")
            ).first()
            if not transaction_option:
                raise TransactionOption.DoesNotExist

            serializer = TransactionOptionRetrieveSerializer(
                instance=transaction_option
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except TransactionOption.DoesNotExist:
            return Response(
                data={"message": "transaction option not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs) -> Response:
        try:
            transaction_option: TransactionOption = TransactionOption.objects.filter(
                transaction_uuid=kwargs.get("transaction_uuid")
            ).first()
            if not transaction_option:
                raise TransactionOption.DoesNotExist

            serializer = TransactionOptionUpdateSerializer(
                instance=transaction_option, data=request.data
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
        except TransactionOption.DoesNotExist:
            return Response(
                data={"message": "transaction option not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )