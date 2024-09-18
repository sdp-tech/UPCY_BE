from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsReformer
from market.models import Market
from rest_framework import status
from market.serializers.market_service_serializer import MarketServiceSerializer

class MarketServiceView(APIView):
    permission_classes = [IsReformer]

    def post(self, request, market_uuid):
        market = Market.objects.filter(market_uuid=market_uuid).first()
        if not market:
            return Response(
                data={'message': 'market not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serialized = MarketServiceSerializer(data=request.data, context={'market': market})
        serialized.is_valid(raise_exception=True)
        reform_service = serialized.save()
        return Response(
            data={"service_uuid": reform_service.service_uuid},
            status=status.HTTP_201_CREATED
        )

class MarketServiceImageUploadView(APIView):
    permission_classes = [IsReformer]

    def post(self, request):
        pass

    def put(self, request):
        pass