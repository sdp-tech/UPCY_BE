from rest_framework import serializers

from users.models.user import User


class UserOrderInformationSerializer(serializers.ModelSerializer):
    orderer_name = serializers.SerializerMethodField(read_only=True)
    orderer_phone_number = serializers.SerializerMethodField(read_only=True)
    orderer_email = serializers.SerializerMethodField(read_only=True)
    orderer_address = serializers.SerializerMethodField(read_only=True)

    def get_orderer_name(self, obj):
        return obj.full_name

    def get_orderer_phone_number(self, obj):
        return obj.phone

    def get_orderer_email(self, obj):
        return obj.email

    def get_orderer_address(self, obj):
        return obj.address

    class Meta:
        model = User
        fields = [
            "orderer_name",
            "orderer_phone_number",
            "orderer_email",
            "orderer_address",
        ]


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
