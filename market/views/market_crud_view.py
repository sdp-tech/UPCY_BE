from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsReformer
from market.models import Market
from market.serializers.market_serializer import MarketSerializer
from users.models import ReformerProfile
from rest_framework import status


class MarketCrudView(APIView):
    permission_classes = [IsReformer] # Reformer의 경우에만 해당 API 사용 가능

    def get(self, request):
        try:
            market = Market.objects.filter(reformer__user=request.user).select_related('reformer').first()
            if not market:
                return Response(
                    data={'message': 'market not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serialized = MarketSerializer(instance=market)
            return Response(
                data=serialized.data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                data={'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def post(self, request):
        # 리포머 프로필이 존재하는지 확인
        reformer = ReformerProfile.objects.filter(user=request.user).first()
        if not reformer:
            return Response(
                data={'message': 'reformer not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 이미 마켓이 존재하는지 검증
        market = Market.objects.filter(reformer=reformer).first()
        if market:
            return Response(
                data={'message': 'market already exists'},
                status=status.HTTP_409_CONFLICT
            )

        serialized = MarketSerializer(data=request.data, context={'reformer': reformer})
        serialized.is_valid(raise_exception=True)
        serialized.save()
        return Response(
            data=serialized.data,
            status=status.HTTP_201_CREATED
        )
