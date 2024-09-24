from rest_framework import serializers

from market.models import ServiceMaterial


class ServiceMaterialRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMaterial
        fields = ['material_uuid', 'material_name']
