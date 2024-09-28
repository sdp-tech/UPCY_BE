from rest_framework import serializers

from users.models.reformer import Reformer


class ReformerUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model=Reformer
        fields=['reformer_link', 'reformer_area']
        extra_kwargs = {
            'reformer_link': {'required': False},
            'reformer_area': {'required': False},
        }

    def validate(self, attrs):
        if "reformer_link" in attrs and attrs["reformer_link"] == self.instance.reformer_link:
            raise serializers.ValidationError("reformer_link must be different")

        if "reformer_area" in attrs and attrs["reformer_area"] == self.instance.reformer_area:
            raise serializers.ValidationError("reformer_area must be different")

        return attrs

    def update(self, instance, validated_data):
        instance.reformer_link = validated_data.get('reformer_link', instance.reformer_link)
        instance.reformer_area = validated_data.get('reformer_area', instance.reformer_area)
        instance.save()
        return instance
