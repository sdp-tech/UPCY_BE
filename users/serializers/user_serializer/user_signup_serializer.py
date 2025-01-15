from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models.user import User


def validate_password_field(password):
    try:
        validate_password(password)
    except serializers.ValidationError:
        raise serializers.ValidationError("Invalid password format")
    return password


class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def validate_nickname(self, value):
        if value == "":
            raise serializers.ValidationError("Nickname cannot be empty.")
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("Nickname already in use.")
        return value

    def validate_password(self, value):
        return validate_password_field(value)

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
