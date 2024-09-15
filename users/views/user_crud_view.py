from tokenize import TokenError

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken

from users.services import UserService
from users.serializers.user_information_serializer import UserInformationSerializer


class UserCrudApi(APIView):
    permission_classes = [IsAuthenticated]
    service = UserService()

    def get(self, request):
        user = request.user
        serialized = UserInformationSerializer(instance=user)
        return Response(
            data=serialized.data,
            status=status.HTTP_200_OK
        )

    def put(self, request):
        return Response(
            data={
                "message": "Not implemented yet"
            },
            status=status.HTTP_501_NOT_IMPLEMENTED
        )

    def delete(self, request):
        user = request.user
        refresh_token = request.data.get('refresh_token')
        try:
            self.service.logout(refresh_token=refresh_token) # Refresh Token 만료 처리
            self.service.delete_user(user) # 사용자 삭제

            return Response(
                data={"message": "Successfully deleted user"},
                status=status.HTTP_204_NO_CONTENT
            )
        except (TokenError, InvalidToken) as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
