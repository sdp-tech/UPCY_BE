from rest_framework import serializers
from market.models import ServiceStyle

class ServiceStyleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStyle
        fields = ['style_name', 'description', 'price', 'available']

    def update(self, instance, validated_data):

        instance.style_name = validated_data.get('style_name', instance.style_name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.available = validated_data.get('available', instance.available)


        instance.save()
        return instance
