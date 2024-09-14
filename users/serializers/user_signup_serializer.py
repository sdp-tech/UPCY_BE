from rest_framework import serializers

from users.models import User


class UserSignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    agreement_terms = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError("User that using this email already exists.")

        if attrs["agreement_terms"] == "False":
            raise serializers.ValidationError("Agreement terms must be accepted.")

        return attrs
