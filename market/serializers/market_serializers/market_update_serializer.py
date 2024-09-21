from rest_framework import serializers

from market.models import Market


class MarketUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Market
        fields = ['market_name', 'market_introduce', 'market_address']
        extra_kwargs = {
            'market_name': {'required': False},
            'market_introduce': {'required': False},
            'market_address': {'required': False},
        }

    def update(self, instance, validated_data):
        instance.market_name = validated_data.get('market_name', instance.market_name)
        instance.market_introduce = validated_data.get('market_introduce', instance.market_introduce)
        instance.market_address = validated_data.get('market_address', instance.market_address)
        instance.save()
        return instance
