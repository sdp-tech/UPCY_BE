# market/views/report_views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from market.models import Report
from market.serializers.report_serializer.reporter_serializer import ReportSerializer
from users.models.user import User


class ReportUserView(APIView):
    def post(self, request):
        data = request.data
        try:
            reported_user = User.objects.get(id=data["reported_user_id"])
            reporter_user = User.objects.get(id=request.user.id)

            report: Report = Report.objects.create(
                reported_user=reported_user,
                reporter_user=reporter_user,
                reason=data["reason"],
                details=data.get("details", ""),
            )
            serializer = ReportSerializer(instance=report)

            report_count = Report.objects.filter(reported_user=reported_user).count()
            serializer.data["report_count"] = report_count

            if report_count >= 5:
                reported_user.is_active = False
                reported_user.save()

                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response(
                {"status": "error", "message": "사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"status": "error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
