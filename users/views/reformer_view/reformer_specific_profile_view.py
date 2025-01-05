from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from users.models.user import User
from users.models.reformer import Reformer
from users.serializers.reformer_serializer.reformer_profile_serializer import (
    ReformerProfileSerializer,
)
from users.services import UserService

class ReformerSpecificProfileView(APIView):
    permission_classes = [AllowAny,]

    def get(self, request, email:str) -> Response:
        try:
            user = User.objects.get(email=email)
            reformer_profile = Reformer.objects.get(user=user)
            if not reformer_profile:
                raise Reformer.DoesNotExist(
                    "해당 사용자는 리포머 프로필이 등록되어 있지 않습니다."
                )
            serializer = ReformerProfileSerializer(
                instance=reformer_profile, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Reformer.DoesNotExist as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
