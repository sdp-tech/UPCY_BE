from rest_framework import serializers
from users.models import User


class UserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'phone', 'nickname', 'agreement_terms', 'address',
                  'is_active', 'role']
