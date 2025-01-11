from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models.reformer import Reformer
from users.models.user import User


class ReformerEmailView(APIView):
    permission_classes = [
        AllowAny,
    ]

    def get(self, request, nickname: str) -> Response:
        try:
            user = User.objects.get(nickname=nickname)
            # check if the user is a reformer
            reformer_profile = Reformer.objects.get(user=user)
            if not reformer_profile:
                raise Reformer.DoesNotExist(
                    "해당 사용자는 리포머 프로필이 등록되어 있지 않습니다."
                )
            return Response({"email": user.email}, status=status.HTTP_200_OK)
        except User.DoesNotExist as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
