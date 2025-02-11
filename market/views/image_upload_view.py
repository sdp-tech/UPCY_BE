from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import view_exception_handler
from core.permissions import IsReformer
from market.models import Market, Service, ServiceOption
from market.services import MarketImageUploadService


class MarketImageUploadView(APIView):
    permission_classes = [IsReformer]
    service = MarketImageUploadService()

    @view_exception_handler
    def post(self, request, **kwargs):
        market = (
            Market.objects.filter(
                reformer__user=request.user, market_uuid=kwargs.get("market_uuid")
            )
            .select_related("reformer")
            .first()
        )
        if not market:
            raise ObjectDoesNotExist("Cannot found market with this uuid")

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


class MarketServiceImageUploadView(APIView):
    permission_classes = [IsReformer]
    service = MarketImageUploadService()

    @view_exception_handler
    def post(self, request, **kwargs):
        market_service = (
            Service.objects.filter(
                market__market_uuid=kwargs.get("market_uuid"),
                service_uuid=kwargs.get("service_uuid"),
            )
            .select_related("market")
            .first()
        )
        if not market_service:
            raise ObjectDoesNotExist("Cannot found service object with these uuids")

        image_file = request.FILES.get(
            "service_image"
        )  # 이미지 파일 리스트를 request body에서 획득
        if not image_file:
            raise ValidationError("There are no image files to upload")

        self.service.upload_service_images(entity=market_service, image_file=image_file)
        return Response(
            data={"message": "Successfully uploaded service image"},
            status=status.HTTP_200_OK,
        )


class ServiceOptionImageUploadView(APIView):
    permission_classes = [IsReformer]
    service = MarketImageUploadService()

    @view_exception_handler
    def post(self, request, **kwargs):
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
            raise ObjectDoesNotExist("Cannot found service option with these uuids")

        image_files = request.FILES.getlist(
            "option_image"
        )  # 이미지 파일 리스트를 request body에서 획득
        if not image_files:
            raise ValidationError("There are no image files to upload")

        self.service.upload_service_option_images(
            entity=market_service_option, image_files=image_files
        )

        return Response(
            data={"message": "Successfully uploaded service option image"},
            status=status.HTTP_200_OK,
        )
