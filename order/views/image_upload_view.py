from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsCustomer
from order.models import Order
from order.services import OrderImageUploadService

class OrderImageUploadView(APIView):
    permission_classes = [IsCustomer]
    order = OrderImageUploadService()

    def post(self, request, **kwargs):
        try:
            order = (
                Order.objects.filter(
                    service_uuid = kwargs.get("service_uuid"),
                    order_uuid = kwargs.get("order_uuid"),
                )
                .select_related("service")
                .first()
            )
            if not order:
                raise Order.DoesNotExist

            image_files = request.FILES.getlist(
                "order_image"
            )

            if not image_files:
                raise ValidationError("There are no image files to upload")

            self.order.upload_order_images(order, image_files)
            return Response(
                data={"message": "Successfully uploaded order image"},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Order.DoesNotExist:
            return Response(
                data={"message": "order not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OrderAdditionalImageUploadView(APIView):
    permission_classes = [IsCustomer]
    order = OrderImageUploadService()

    def post(self, request, **kwargs):
        try:
            order_additional_option = (
                Order.objects.filter(
                    service_uuid = kwargs.get("service_uuid"),
                    order_uuid = kwargs.get("order_uuid"),
                    additional_uuid=kwargs.get("additional_uuid")
                )
                .select_related("service")
                .first()
            )
            if not order_additional_option:
                raise Order.DoesNotExist

            image_files = request.FILES.getlist(
                "additional_image"
            )
            if not image_files:
                raise ValidationError("There are no image files to upload")
            self.order.upload_order_images(
                entity=order_additional_option, image_files=image_files
            )
            return Response(
                data={"message": "Successfully uploaded order additional image"},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Order.DoesNotExist:
            return Response(
                data={"message": "order additional option not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

