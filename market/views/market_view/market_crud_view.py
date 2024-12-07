import os

from boto3 import client
from botocore.client import BaseClient
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import view_exception_handler
from core.permissions import IsReformer
from market.models import Market
from market.serializers.market_serializers.market_serializer import MarketSerializer
from market.serializers.market_serializers.market_update_serializer import (
    MarketUpdateSerializer,
)


class MarketCrudView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.method in ["POST", "PUT", "DELETE"]:
            return [IsReformer()]
        return super().get_permissions()

    @view_exception_handler
    def get(self, request, **kwargs) -> Response:
        """
        market uuid에 해당하는 마켓 정보를 반환하는 API
        """
        market: Market = Market.objects.get_market_by_market_uuid_related_to_reformer(
            market_uuid=kwargs.get("market_uuid")
        )
        serializer: MarketSerializer = MarketSerializer(instance=market)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @view_exception_handler
    def put(self, request, **kwargs) -> Response:
        market: Market = Market.objects.get_market_by_market_uuid_related_to_reformer(
            market_uuid=kwargs.get("market_uuid")
        )

        serializer: MarketUpdateSerializer = MarketUpdateSerializer(
            instance=market, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data={"message": "market updated"}, status=status.HTTP_200_OK)

    @view_exception_handler
    def delete(self, request, **kwargs) -> Response:
        market: Market = Market.objects.get_market_by_market_uuid_related_to_reformer(
            market_uuid=kwargs.get("market_uuid")
        )

        with transaction.atomic():
            if market.market_thumbnail:
                s3: BaseClient = client("s3")
                s3.delete_object(
                    Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                    Key=market.market_thumbnail.name,
                )

            market.delete()
            return Response(
                data={"message": "market deleted"},
                status=status.HTTP_200_OK,
            )
