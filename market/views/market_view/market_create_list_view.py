from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsReformer
from django.core.exceptions import ObjectDoesNotExist
from market.models import Market
from market.serializers.market_serializers.market_serializer import MarketSerializer
from users.models.reformer import Reformer


class MarketCreateListView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method == "POST":
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request) -> Response:
        try:
            market = Market.objects.filter(reformer__user=request.user).select_related(
                "reformer"
            ).first()
            if not market:  # 마켓이 존재하지 않으면, 에러처리
                raise Market.DoesNotExist("리포머가 생성한 마켓이 존재하지 않습니다.")

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

    def post(self, request) -> Response:
        try:
            # 리포머 프로필이 존재하는지 확인
            reformer = Reformer.objects.filter(user=request.user).first()
            if not reformer:
                raise Reformer.DoesNotExist("리포머 프로필이 존재하지 않습니다. 리포머 사용자만 호출 가능합니다.")

            # 리포머가 생성한 마켓이 몇개인지 확인
            if Market.objects.filter(reformer=reformer).exists():
                # 리포머 한명이 생성할 수 있는 마켓은 최대 1개
                raise ValidationError(
                    "리포머는 최대 1개의 마켓 까지만 생성이 가능합니다."
                )

            serialized = MarketSerializer(
                data=request.data, context={"reformer": reformer}
            )
            serialized.is_valid(raise_exception=True)
            serialized.save()
            return Response(data=serialized.data, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
