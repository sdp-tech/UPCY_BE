from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsReformer
from order.models import Order
from order.serializers.order_serializers.order_update_serializer import (
    OrderUpdateSerializer,
)


class OrderUpdateView(APIView):
    """
    Reformer가 요청받은 주문서를 수정할 수 있는 뷰
    """

    permission_classes = [IsReformer]  # Reformer 권한만 접근 가능

    def get_object(self, order_uuid, reformer):
        # Reformer가 요청받은 주문서인지 확인하는 쿼리셋
        return (
            Order.objects.filter(
                order_uuid=order_uuid, service__market__reformer=reformer
            )
            .select_related("request_user", "service", "service__market")
            .first()
        )

    def put(self, request, **kwargs) -> Response:
        try:
            order_uuid = kwargs.get("order_uuid")
            reformer = request.user.reformer_profile  # 현재 Reformer 사용자

            # Reformer와 관련된 주문서 객체 가져오기
            order = self.get_object(order_uuid, reformer)
            if not order:
                return Response(
                    data={"message": "Order not found or access denied"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 직렬화 및 유효성 검사
            serialized = OrderUpdateSerializer(
                instance=order, data=request.data, partial=True
            )
            serialized.is_valid(raise_exception=True)
            serialized.save()

            return Response(
                data={"message": "Order updated successfully"},
                status=status.HTTP_200_OK,
            )

        except Order.DoesNotExist:
            return Response(
                data={"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
