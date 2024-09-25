from rest_framework import serializers

from users.models.user import User


class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError("User that using this email already exists.")

        if attrs["password"] is None or attrs["password"] == '':
            raise serializers.ValidationError("Password is required.")

        if not attrs["agreement_terms"]:
            raise serializers.ValidationError("Agreement terms must be accepted.")

        return attrs

    class Meta:
        model = User
        fields = ['email', 'password', 'nickname', 'agreement_terms', 'introduce']
        extra_kwargs = {
            'email': {'required': True},
            'password': {'required': True},
            'nickname': {'required': True},
            'agreement_terms': {'required': True},
            'introduce': {'required': False}
        }
