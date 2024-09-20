from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsReformer
from market.models import MarketService
from market.serializers.market_service_serializer import MarketServiceRetrieveSerializer
from rest_framework import status


class MarketServiceCrudView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method in ['POST', 'PUT', 'DELETE']:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs) -> Response:
        try:
            market_service = MarketService.objects.filter(
                market__market_uuid=kwargs.get('market_uuid'),
                service_uuid=kwargs.get('service_uuid')
            ).select_related('market').first()
            if not market_service:
                raise MarketService.DoesNotExist

            serialized = MarketServiceRetrieveSerializer(instance=market_service)
            return Response(
                data=serialized.data,
                status=status.HTTP_200_OK
            )
        except MarketService.DoesNotExist:
            return Response(
                data={'message': 'market service not found'},
                status=status.HTTP_404_NOT_FOUND
            )
