from typing import Any, List

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from market.models import (
    Service,
    ServiceImage,
    ServiceMaterial,
    ServiceOption,
    ServiceStyle,
)
from market.serializers.service_serializers.service_option.service_option_retrieve_serializer import (
    ServiceOptionRetrieveSerializer,
)
from users.serializers.reformer_serializer.reformer_profile_serializer import (
    ReformerProfileSerializer,
)


class ServiceStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStyle
        fields = ["style_uuid", "style_name"]


class ServiceMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMaterial
        fields = ["material_uuid", "material_name"]


class ServiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOption
        fields = ["option_uuid", "option_name", "option_content", "option_price"]


class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImage
        fields = ["image"]


class ServiceCreateSerializer(serializers.ModelSerializer):
    service_option = ServiceOptionSerializer(many=True)
    service_style = ServiceStyleSerializer(many=True)
    service_material = ServiceMaterialSerializer(many=True)

    class Meta:
        model = Service
        fields = [
            "service_uuid",
            "service_title",
            "service_content",
            "service_category",
            "service_style",
            "service_period",
            "basic_price",
            "max_price",
            "service_option",
            "service_material",
            "temporary",
        ]
        extra_kwargs = {
            "service_uuid": {"read_only": True},
            "service_title": {"write_only": True},
            "service_content": {"write_only": True},
            "service_category": {"write_only": True},
            "service_period": {"write_only": True},
            "basic_price": {"write_only": True},
            "max_price": {"write_only": True},
            "temporary": {"write_only": True},
        }

    def to_representation(self, instance):
        return {
            "service_uuid": instance.service_uuid,
            "service_options": [
                {
                    "option_uuid": option.option_uuid,
                    "option_name": option.option_name,
                }
                for option in instance.service_option.all()
            ],
            "service_materials": [
                {
                    "material_uuid": material.material_uuid,
                    "material_name": material.material_name,
                }
                for material in instance.service_material.all()
            ],
            "service_styles": [
                {
                    "style_uuid": style.style_uuid,
                    "style_name": style.style_name,
                }
                for style in instance.service_style.all()
            ],
        }

    def create(self, validated_data):
        service_style = validated_data.pop("service_style")
        service_option = validated_data.pop("service_option")
        service_material = validated_data.pop("service_material")

        market = self.context.get("market")
        market_service = Service.objects.create(market=market, **validated_data)
        market_service.save()

        for style in service_style:
            service_style = ServiceStyle.objects.create(
                market_service=market_service, **style
            )
            service_style.save()

        for option in service_option:
            service_option = ServiceOption.objects.create(
                market_service=market_service, **option
            )
            service_option.save()

        for material in service_material:
            service_material = ServiceMaterial.objects.create(
                market_service=market_service, **material
            )
            service_material.save()

        return market_service


class ServiceRetrieveSerializer(serializers.ModelSerializer):
    reformer_info = serializers.SerializerMethodField(read_only=True)
    service_option = ServiceOptionRetrieveSerializer(many=True)
    service_style = ServiceStyleSerializer(many=True)
    service_material = ServiceMaterialSerializer(many=True)
    service_image = ServiceImageSerializer(many=True)
    market_uuid = serializers.ReadOnlyField(
        source="market.market_uuid"
    )  # https://www.django-rest-framework.org/api-guide/fields/#readonlyfield

    def get_reformer_info(self, obj):
        return ReformerProfileSerializer(obj.market.reformer).data

    def get_service_option_images(self, obj) -> List[Any]:
        images = []
        for service_option in obj.service_option.all():
            for service_option_image in service_option.service_option_image.all():
                images.append({"image": service_option_image.image.url})
        return images

    class Meta:
        model = Service
        fields = [
            "reformer_info",
            "market_uuid",
            "service_uuid",
            "service_title",
            "service_content",
            "service_category",
            "service_style",
            "service_period",
            "basic_price",
            "max_price",
            "service_option",
            "service_material",
            "service_image",
            "suspended",
            "temporary",
            "created",
            "updated",
        ]
