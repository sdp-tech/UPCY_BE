from rest_framework import serializers

from market.models import Market

from rest_framework import serializers
from market.models import Report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['reported_user', 'reporter_user', 'reason', 'details']


class MarketSerializer(serializers.ModelSerializer):
    market_uuid = serializers.UUIDField(read_only=True)
    market_thumbnail = serializers.FileField(use_url=True, read_only=True)

    class Meta:
        model = Market
        fields = [
            "market_uuid",
            "market_name",
            "market_introduce",
            "market_address",
            "market_thumbnail",
        ]

    def create(self, validated_data):
        market = Market.objects.create(
            reformer=self.context.get("reformer"), **validated_data
        )
        market.save()
        return market
