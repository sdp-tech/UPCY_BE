from rest_framework import serializers
from market.models import Report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['reported_user', 'reporter_user', 'reason', 'details']
