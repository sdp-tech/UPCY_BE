from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import view_exception_handler
from core.permissions import IsReformer
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

    @view_exception_handler
    def get(self, request) -> Response:
        market: Market = Market.objects.get_market_by_user_related_to_reformer(
            user=request.user
        )
        serializer: MarketSerializer = MarketSerializer(instance=market)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @view_exception_handler
    def post(self, request) -> Response:
        # 리포머 프로필이 존재하는지 확인
        # reformer: Reformer = Reformer.objects.select_related("user").filter(user=request.user).first()
        reformer: Reformer = getattr(
            request.user, "reformer_profile", None
        )  # 이렇게 하면 쿼리자체의 길이를 줄일 수 있음 (더 깔끔)
        if not reformer:
            raise ObjectDoesNotExist("Reformer not found")

        # 리포머가 생성한 마켓이 이미 존재하는지 확인
        if Market.objects.check_if_market_exists(
            reformer=reformer
        ):  # 이미 마켓 인스턴스가 리포머에 대해 존재한다면 유효하지 않은 요청
            raise ValidationError("This reformer has already created a market.")

        serializer = MarketSerializer(data=request.data, context={"reformer": reformer})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
