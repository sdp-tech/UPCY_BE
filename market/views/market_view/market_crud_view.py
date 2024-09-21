from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsReformer
from market.models import Market
from market.serializers.market_serializers.market_serializer import MarketSerializer
from market.serializers.market_serializers.market_update_serializer import MarketUpdateSerializer


class MarketCrudView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method in ['POST', 'PUT', 'DELETE']:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs) -> Response:
        try:
            market = Market.objects.filter(
                reformer__user=request.user,
                market_uuid=kwargs.get('market_uuid')
            ).select_related('reformer').first()
            if not market:
                raise Market.DoesNotExist

            serialized = MarketSerializer(instance=market)
            return Response(
                data=serialized.data,
                status=status.HTTP_200_OK
            )
        except Market.DoesNotExist:
            return Response(
                data={'message': 'market not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs) -> Response:
        try:
            market = Market.objects.filter(
                reformer__user=request.user,
                market_uuid=kwargs.get('market_uuid')
            ).select_related('reformer').first()
            if not market:
                raise Market.DoesNotExist

            serialized = MarketUpdateSerializer(instance=market, data=request.data)
            if serialized.is_valid(raise_exception=True):
                serialized.save()
                return Response(
                    data={'message': 'market updated'},
                    status=status.HTTP_200_OK
                )
        except Market.DoesNotExist:
            return Response(
                data={'message': 'market not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, **kwargs):
        try:
            market = Market.objects.filter(
                reformer__user=request.user,
                market_uuid=kwargs.get('market_uuid')
            ).select_related('reformer').first()
            if not market:
                raise Market.DoesNotExist

            market.delete()
            return Response(
                data={'message': 'market deleted'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Market.DoesNotExist:
            return Response(
                data={'message': 'market not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
