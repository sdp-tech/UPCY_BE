from rest_framework import serializers

from users.models.user import User


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)  # 요청시에만 사용하는 필드
    password = serializers.CharField(write_only=True)  # 요청시에만 사용하는 필드

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # 이메일과 비밀번호가 입력되었는지 확인
        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")

        # 사용자가 존재하는지 확인
        user = User.objects.filter(email=email).first()
        if not user:
            raise User.DoesNotExist("No user found with this email address.")

        # 비밀번호 확인
        if not user.check_password(password):
            raise serializers.ValidationError("The password is incorrect.")

        # 검증이 성공적으로 완료된 경우 사용자 객체 반환
        attrs["user"] = user
        return attrs
