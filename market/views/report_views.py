# market/views/report_views.py
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from core.exceptions import view_exception_handler
from market.serializers.report_serializer.reporter_serializer import ReportSerializer
from users.models.user import User


class ReportUserView(APIView):

    @view_exception_handler
    def post(self, request):
        # 신고대상
        reported_user_id: str = request.data.get("reported_user_id")
        if not reported_user_id:
            raise ValidationError("reported_user_id is required")
        reported_user: User = User.objects.filter(id=reported_user_id).first()
        if not reported_user:
            raise NotFound("reported_user does not exist")

        # 신고자
        reporter: User = request.user

        # 신고 인스턴스 생성 및 신고 횟수 누적
        data = request.data.copy()
        data.pop("reported_user_id", None)
        serializer = ReportSerializer(
            data=request.data,
            context={"reporter": reporter, "reported_user": reported_user},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
