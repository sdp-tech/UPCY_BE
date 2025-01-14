from rest_framework import serializers

from market.models import Market


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
        return Market.objects.create(
            reformer=self.context.get("reformer"), **validated_data
        )
