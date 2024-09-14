from rest_framework import serializers

from users.models import User


class UserSignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError("User that using this email already exists.")

        if attrs["password"] != attrs["re_password"]:
            raise serializers.ValidationError("Passwords do not match.")

        return attrs
