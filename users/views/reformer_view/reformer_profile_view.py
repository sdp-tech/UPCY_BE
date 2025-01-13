from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import view_exception_handler
from users.models.reformer import Reformer
from users.serializers.reformer_serializer.reformer_profile_serializer import (
    ReformerProfileSerializer,
)
from users.serializers.reformer_serializer.reformer_update_serializer import (
    ReformerUpdateSerializer,
)
from users.services import UserService


class ReformerProfileView(APIView):
    permission_classes = [IsAuthenticated]
    user_service = UserService()

    @view_exception_handler
    def get(self, request) -> Response:
        user = request.user  # 요청한 사용자 정보를 가져온다.
        reformer_profile = Reformer.objects.filter(
            user=user
        ).first()  # 사용자의 프로필에 연결되어 있는 리포머 프로필 데이터를 가져온다.
        if not reformer_profile:  # 없다면 Exception
            raise Reformer.DoesNotExist(
                "해당 사용자는 리포머 프로필이 등록되어 있지 않습니다."
            )

        serializer = ReformerProfileSerializer(
            instance=reformer_profile, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @view_exception_handler
    def post(self, request) -> Response:
        user = request.user
        serializer = ReformerProfileSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid()
        serializer.save()
        self.user_service.update_user_role(
            user=user, role="reformer"
        )  # Reformer 프로필 등록 -> user role 변경
        return Response(
            data={"message": "successfully created"},
            status=status.HTTP_201_CREATED,
        )

    @view_exception_handler
    def put(self, request) -> Response:
        user = request.user
        reformer_profile = Reformer.objects.filter(user=user).first()
        if not reformer_profile:
            raise ObjectDoesNotExist("There is no reformer profile for this user.")

        serializer = ReformerUpdateSerializer(
            instance=reformer_profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data={"message": "successfully updated"}, status=status.HTTP_200_OK
        )

    @view_exception_handler
    def delete(self, request):
        user = request.user
        reformer_profile = Reformer.objects.filter(user=user).first()
        if not reformer_profile:
            raise ObjectDoesNotExist("리포머 프로필이 등록되어 있지 않습니다.")

        with transaction.atomic():
            reformer_profile.delete()
            self.user_service.update_user_role(
                user=user, role="user"
            )  # reformer 프로필 삭제 -> user role 변경
            return Response(
                data={"message": "successfully deleted"}, status=status.HTTP_200_OK
            )
