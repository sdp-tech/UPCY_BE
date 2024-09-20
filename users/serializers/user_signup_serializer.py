from rest_framework import serializers

from users.models.user import User


class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError("User that using this email already exists.")

        if not attrs["agreement_terms"]:
            raise serializers.ValidationError("Agreement terms must be accepted.")

        return attrs

    class Meta:
        model = User
        fields = ['email', 'password', 'phone', 'nickname', 'agreement_terms', 'address']
        extra_kwargs = {
            'email': {'required': True},
            'phone': {'required': True},
            'nickname': {'required': True},
            'agreement_terms': {'required': True},
            'address': {'required': True},
        }
