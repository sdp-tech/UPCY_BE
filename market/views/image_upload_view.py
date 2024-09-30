from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsReformer
from market.models import Market, Service, ServiceOption
from market.services import MarketImageUploadService


class MarketImageUploadView(APIView):
    permission_classes = [IsReformer]
    service = MarketImageUploadService()

    def post(self, request, **kwargs):
        try:
            market = (
                Market.objects.filter(
                    reformer__user=request.user, market_uuid=kwargs.get("market_uuid")
                )
                .select_related("reformer")
                .first()
            )
            if not market:
                raise Market.DoesNotExist

            image_file = request.FILES.get(
                "thumbnail_image"
            )  # 이미지 파일 request body에서 획득
            if not image_file:
                raise ValidationError("Image file not found")

            self.service.upload_market_image(market, image_file)
            return Response(
                data={"message": "Successfully uploaded market thumbnail image"},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Market.DoesNotExist:
            return Response(
                data={"message": "market not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MarketServiceImageUploadView(APIView):
    permission_classes = [IsReformer]
    service = MarketImageUploadService()

    def post(self, request, **kwargs):
        try:
            market_service = (
                Service.objects.filter(
                    market__market_uuid=kwargs.get("market_uuid"),
                    service_uuid=kwargs.get("service_uuid"),
                )
                .select_related("market")
                .first()
            )
            if not market_service:
                raise Service.DoesNotExist

            image_files = request.FILES.getlist(
                "service_images"
            )  # 이미지 파일 리스트를 request body에서 획득
            if not image_files:
                raise ValidationError("There are no image files to upload")

            self.service.upload_service_images(market_service, image_files)
            return Response(
                data={"message": "Successfully uploaded service image"},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Service.DoesNotExist:
            return Response(
                data={"message": "market service not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ServiceOptionImageUploadView(APIView):
    permission_classes = [IsReformer]
    service = MarketImageUploadService()

    def post(self, request, **kwargs):
        try:
            market_service_option = (
                ServiceOption.objects.filter(
                    market_service__market__market_uuid=kwargs.get("market_uuid"),
                    market_service__service_uuid=kwargs.get("service_uuid"),
                    option_uuid=kwargs.get("option_uuid"),
                )
                .select_related("market_service")
                .first()
            )
            if not market_service_option:
                raise Service.DoesNotExist

            image_files = request.FILES.getlist(
                "option_image"
            )  # 이미지 파일 리스트를 request body에서 획득
            if not image_files:
                raise ValidationError("There are no image files to upload")
            self.service.upload_service_images(
                entity=market_service_option, image_files=image_files
            )

            return Response(
                data={"message": "Successfully uploaded service option image"},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Service.DoesNotExist:
            return Response(
                data={"message": "market service option not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
