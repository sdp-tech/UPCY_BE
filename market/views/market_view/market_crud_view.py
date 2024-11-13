import os

from boto3 import client
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

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

    def get(self, request, **kwargs) -> Response:
        """
        market uuid에 해당하는 마켓 정보를 반환하는 API
        """
        try:
            market = (
                Market.objects.filter(market_uuid=kwargs.get("market_uuid"))
                .select_related("reformer")
                .first()
            )
            if not market:
                raise Market.DoesNotExist

            serialized = MarketSerializer(instance=market)
            return Response(data=serialized.data, status=status.HTTP_200_OK)
        except Market.DoesNotExist:
            return Response(
                data={"message": "market not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs) -> Response:
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

            serialized = MarketUpdateSerializer(instance=market, data=request.data)
            if serialized.is_valid(raise_exception=True):
                serialized.save()
                return Response(
                    data={"message": "market updated"}, status=status.HTTP_200_OK
                )
        except Market.DoesNotExist:
            return Response(
                data={"message": "market not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, **kwargs):
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

            with transaction.atomic():
                s3 = client("s3")
                s3.delete_object(
                    Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                    Key=market.market_thumbnail.name,
                )
                market.delete()
                return Response(
                    data={"message": "market deleted"},
                    status=status.HTTP_204_NO_CONTENT,
                )
        except Market.DoesNotExist:
            return Response(
                data={"message": "market not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
