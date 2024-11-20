from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsCustomer, IsReformer
from order.models import AdditionalImage, Order, OrderImage
from order.serializers.order_serializers.order_create_retrieve_serializer import (
    OrderImageSerializer,
)
from order.services import OrderImageUploadService

# 이미지도 추가나 삭제가 가능하도록 PUT이랑 DELETE 추가하는 게 좋지 않을까요?


class OrderImageView(APIView):
    """
    주문서 이미지 업로드 및 조회 뷰
    """

    permission_classes = [IsCustomer]
    service = OrderImageUploadService()

    def get_permissions(self):
        # GET 요청일 때는 Reformer와 Customer 모두 접근 가능
        if self.request.method == "GET":
            return [IsAuthenticated()]
        # POST 요청일 때는 Customer만 접근 가능
        elif self.request.method == "POST":
            return [IsCustomer()]
        return super().get_permissions()

    def get(self, request, **kwargs):
        """
        특정 주문서에 연결된 주문 이미지를 조회하는 GET 메서드
        """
        try:
            # 주문서 객체 조회
            order = (
                Order.objects.filter(
                    order_uuid=kwargs.get("order_uuid"), request_user=request.user
                )
                .select_related("service")
                .first()
            )

            # 주문서에 연결된 이미지들 조회
            order_images = OrderImage.objects.filter(service_order=order)
            serialized = OrderImageSerializer(order_images, many=True)

            return Response(data=serialized.data, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response(
                data={"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, **kwargs):
        """
        특정 주문서에 주문 이미지를 업로드하는 POST 메서드
        """
        try:
            order = (
                Order.objects.filter(
                    order_uuid=kwargs.get("order_uuid"), request_user=request.user
                )
                .select_related("service")
                .first()
            )
            if not order:
                raise Order.DoesNotExist

            # 파일 유효성 검사 후 업로드 서비스 호출
            image_files = request.FILES.getlist("order_image")

            if not image_files:
                raise ValidationError("There are no image files to upload")

            self.service.upload_order_images(order, image_files)

            return Response(
                data={"message": "Order Images uploaded successfully"},
                status=status.HTTP_201_CREATED,
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


class OrderAdditionalImageView(APIView):
    """
    주문서 추가 이미지 업로드 및 조회 뷰
    """

    permission_classes = [IsCustomer]
    service = OrderImageUploadService()

    def get_permissions(self):
        # GET 요청일 때는 Reformer와 Customer 모두 접근 가능
        if self.request.method == "GET":
            return [IsAuthenticated()]
        # POST 요청일 때는 Customer만 접근 가능
        elif self.request.method == "POST":
            return [IsCustomer()]
        return super().get_permissions()

    def get(self, request, **kwargs):
        """
        특정 주문서에 연결된 추가 이미지를 조회하는 GET 메서드
        """
        try:
            order = (
                Order.objects.filter(
                    order_uuid=kwargs.get("order_uuid"), request_user=request.user
                )
                .select_related("service")
                .first()
            )

            order_additional_images = AdditionalImage.objects.filter(
                service_order=order
            )
            serialized = OrderImageSerializer(order_additional_images, many=True)

            return Response(data=serialized.data, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response(
                data={"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, **kwargs):
        """
        특정 주문서에 추가 이미지를 업로드하는 POST 메서드
        """
        try:
            order = (
                Order.objects.filter(
                    order_uuid=kwargs.get("order_uuid"), request_user=request.user
                )
                .select_related("service")
                .first()
            )
            if not order:
                raise Order.DoesNotExist

            # 파일 유효성 검사 후 업로드 서비스 호출
            image_files = request.FILES.getlist("order_additional_image")

            if not image_files:
                raise ValidationError("There are no image files to upload")

            self.service.upload_order_images(order, image_files)

            return Response(
                data={"message": "Addtional Images uploaded successfully"},
                status=status.HTTP_201_CREATED,
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