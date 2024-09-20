from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsReformer
from market.models import Market
from market.serializers.market_serializer import MarketSerializer
from users.models.reformer import Reformer
from rest_framework import status


class MarketCreateListView(APIView):
    permission_classes = [IsReformer] # Reformer의 경우에만 해당 API 사용 가능

    def get(self, request) -> Response:
        try:
            market = Market.objects.filter(reformer__user=request.user).select_related('reformer').first()
            if not market: # 마켓이 존재하지 않으면, 에러처리
                raise Market.DoesNotExist

            serialized = MarketSerializer(instance=market, many=True)
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


    def post(self, request) -> Response:
        try:
            # 리포머 프로필이 존재하는지 확인
            reformer = Reformer.objects.filter(user=request.user).first()
            if not reformer:
                raise Reformer.DoesNotExist

            # 리포머가 생성한 마켓이 몇개인지 확인
            market_count = Market.objects.filter(reformer=reformer).count()
            if market_count >= 5: # 리포머 한명이 생성할 수 있는 마켓은 최대 5개
                raise ValidationError("This reformer exceeds the maximum number of markets")

            serialized = MarketSerializer(data=request.data, context={'reformer': reformer})
            serialized.is_valid(raise_exception=True)
            serialized.save()
            return Response(
                data=serialized.data,
                status=status.HTTP_201_CREATED
            )
        except Reformer.DoesNotExist:
            return Response(
                data={'message': 'reformer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                data={'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
