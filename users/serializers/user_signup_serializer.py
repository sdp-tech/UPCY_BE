from rest_framework import serializers

from users.models import User


class UserSignUpSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError("User that using this email already exists.")

        if attrs["agreement_terms"] == "False":
            raise serializers.ValidationError("Agreement terms must be accepted.")

        return attrs

    class Meta:
        model = User
        fields = ['email', 'password', 'phone', 'nickname', 'agreement_terms', 'address']
