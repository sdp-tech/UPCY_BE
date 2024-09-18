from rest_framework import serializers

from market.models import MarketService, ServiceOption, ServiceMaterial, ServiceStyle


class ServiceStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStyle
        fields = ['style_name']

class ServiceMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMaterial
        fields = ['material_name']

class ServiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOption
        fields = ['option_name', 'option_content', 'option_price']

class MarketServiceSerializer(serializers.ModelSerializer):
    service_option = ServiceOptionSerializer(many=True)
    service_style = ServiceStyleSerializer(many=True)
    service_material = ServiceMaterialSerializer(many=True)

    class Meta:
        model = MarketService
        fields = ['service_title', 'service_content', 'service_category', 'service_style',
                  'service_period', 'basic_price', 'max_price', 'service_option',
                  'service_material']

    def create(self, validated_data):
        service_style = validated_data.pop('service_style')
        service_option = validated_data.pop('service_option')
        service_material = validated_data.pop('service_material')

        market = self.context.get('market')
        market_service = MarketService.objects.create(
            market=market,
            **validated_data
        )
        market_service.save()

        #
        # market_service에 해당하는 service option, service style, service material model 생성
        #

        for style in service_style:
            service_style = ServiceStyle.objects.create(
                market_service=market_service,
                **style
            )
            service_style.save()

        for option in service_option:
            service_option = ServiceOption.objects.create(
                market_service=market_service,
                **option
            )
            service_option.save()

        for material in service_material:
            service_material = ServiceMaterial.objects.create(
                market_service=market_service,
                **material
            )
            service_material.save()

        return market_service
