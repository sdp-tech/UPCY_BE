from rest_framework import serializers

from market.models import Service, ServiceMaterial


class ServiceMaterialCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceMaterial
        fields = ["material_name"]

    def validate(self, attrs):
        service: Service = self.context.get("service")
        if service.service_material.filter(
            material_name=attrs.get("material_name")
        ).exists():  # 역참조 (related_name)
            raise serializers.ValidationError("material name already exists")

        return attrs

    def create(self, validated_data):
        service: Service = self.context.get("service")
        service_material = ServiceMaterial.objects.create(
            market_service=service, **validated_data  # 역참조
        )
        service_material.save()
        return service_material
