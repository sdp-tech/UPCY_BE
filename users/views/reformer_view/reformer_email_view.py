from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models.reformer import Reformer
from users.models.user import User


class ReformerEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, nickname: str) -> Response:
        """
        리포머 닉네임을 사용해서(User 모델의 닉네임) 리포머 정보를 가져오는 API
        """
        user: User = User.objects.filter(nickname=nickname).first()
        reformer_profile = Reformer.objects.get(user=user)
        if not reformer_profile:
            raise Reformer.DoesNotExist(
                "해당 사용자는 리포머 프로필이 등록되어 있지 않습니다."
            )
        return Response({"email": user.email}, status=status.HTTP_200_OK)
