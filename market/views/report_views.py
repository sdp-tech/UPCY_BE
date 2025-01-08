# market/views/report_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from market.models import Report
from market.serializers.report_serializer.ReporterSerializer import ReportSerializer


class ReportUserView(APIView):
    def post(self, request):
        data = request.data
        try:
            reported_user = User.objects.get(id=data['reported_user_id'])
            reporter_user = User.objects.get(id=data['reporter_user_id'])


            report = Report.objects.create(
                reported_user=reported_user,
                reporter_user=reporter_user,
                reason=data['reason'],
                details=data.get('details', '')
            )


            report_count = Report.objects.filter(reported_user=reported_user).count()

           
            if report_count >= 5:
                reported_user.is_active = False
                reported_user.save()

                return Response({
                    "status": "success",
                    "message": "신고가 접수되었으며, 해당 사용자의 서비스가 중단됩니다."
                }, status=status.HTTP_200_OK)

            return Response({
                "status": "success",
                "message": "신고가 접수되었습니다."
            }, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": "사용자를 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)
