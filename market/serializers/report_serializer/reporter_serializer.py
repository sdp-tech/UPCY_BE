from rest_framework import serializers

from market.models import Report
from users.models import User


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["reason", "details"]

    def create(self, validated_data):
        reporter: User = self.context.get("reporter")
        reported_user: User = self.context.get("reported_user")
        report: Report = Report.objects.create(
            reporter_user=reporter, reported_user=reported_user, **validated_data
        )
        reported_user.update_report_count()
        return report
