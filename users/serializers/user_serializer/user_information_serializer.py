from rest_framework import serializers

from users.models.user import User


class UserInformationSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "phone",
            "full_name",
            "nickname",
            "agreement_terms",
            "address",
            "profile_image_url",
            "introduce",
            "is_active",
            "role",
        ]

    def get_profile_image_url(self, obj):
        request = self.context.get("request")
        if request and obj.profile_image and hasattr(obj.profile_image, "url"):
            return request.build_absolute_uri(obj.profile_image.url)
        elif obj.profile_image and hasattr(obj.profile_image, "url"):
            return obj.profile_image.url
        else:
            return None
