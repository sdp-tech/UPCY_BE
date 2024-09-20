from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsReformer
from market.models import Market, MarketService
from rest_framework import status
from market.serializers.market_service_serializer import MarketServiceCreateSerializer, MarketServiceRetrieveSerializer
from market.services import MarketImageUploadService


class MarketServiceView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method in ['POST']:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs):
        try:
            market_service = MarketService.objects.filter(market__market_uuid=kwargs.get('market_uuid')).select_related('market')
            if not market_service:
                raise Market.DoesNotExist

            serialized = MarketServiceRetrieveSerializer(market_service, many=True)
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

    def post(self, request, **kwargs):
        market = Market.objects.filter(market_uuid=kwargs.get('market_uuid')).first()
        if not market:
            return Response(
                data={'message': 'market not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serialized = MarketServiceCreateSerializer(data=request.data, context={'market': market})
        serialized.is_valid(raise_exception=True)
        reform_service = serialized.save()
        return Response(
            data={"service_uuid": reform_service.service_uuid},
            status=status.HTTP_201_CREATED
        )
