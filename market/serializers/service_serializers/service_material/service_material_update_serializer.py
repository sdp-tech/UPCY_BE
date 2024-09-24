from rest_framework import serializers
from market.models import ServiceMaterial

class ServiceMaterialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMaterial
        fields = ['material_name']
        # 나중에 필드 추가되면 extra_kwargs 선언해서 required False로 설정 (PATCH Method)

    def validate(self, attrs):
        if attrs.get('material_name') is None or attrs.get('material_name') == '':
            raise serializers.ValidationError('material name is required')

        if attrs.get('material_name') == self.instance.material_name:
            raise serializers.ValidationError('material name must be different')

        return attrs

    def update(self, instance, validated_data):
        instance.material_name = validated_data.get('material_name', instance.material_name)
        instance.save()
        return instance
