from rest_framework import serializers

from users.models.user import User


class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(
                "User that using this email already exists."
            )

        if attrs["password"] is None or attrs["password"] == "":
            raise serializers.ValidationError("Password is required.")

        return attrs

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "full_name",
            "nickname",
            "agreement_terms",
            "introduce",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "password": {"required": True},
            "full_name": {"required": True},
            "agreement_terms": {"required": True},
            "nickname": {"required": False},
            "introduce": {"required": False},
        }
