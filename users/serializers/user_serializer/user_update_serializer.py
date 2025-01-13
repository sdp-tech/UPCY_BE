from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models.user import User


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["phone", "nickname", "introduce", "address"]
        extra_kwargs = {
            "phone": {"required": False},
            "nickname": {"required": False},
            "introduce": {"required": False},
            "address": {"required": False},
        }

    def validate(self, attrs):
        forbidden_fields = [
            "email",
            "password",
            "agreement_terms",
            "profile_image",
            "is_superuser",
            "is_active",
            "role",
        ]

        for field in forbidden_fields:
            if field in self.initial_data:
                raise ValidationError({field: f"Cannot update '{field}' field."})

        return super().validate(attrs)

    def to_internal_value(self, data):
        """
        User 테이블의 Attribute 중, 업데이트 할 수 있는 필드를 제한하기 위해 사용하는 함수
        """
        known_fields = set(self.fields.keys())  # Meta class에 정의한 fields key list
        incoming_fields = set(data.keys())  # request body에서 들어온 data의 key list

        unknown_fields = incoming_fields - known_fields
        if (
            unknown_fields
        ):  # 만약 위에 정의한 4가지 필드 이외의 필드가 존재하는 경우, 에러 발생
            raise ValidationError(
                {field: "This field is not allowed." for field in unknown_fields}
            )

        return super().to_internal_value(data)
