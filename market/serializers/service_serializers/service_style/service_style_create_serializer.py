from rest_framework import serializers

from market.models import Service, ServiceStyle


class ServiceStyleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStyle
        fields = ["style_name"]

    def validate(self, attrs):  # 데이터의 유효성을 검사하는 메서드
        style_name: str = attrs.get("style_name")
        if style_name == "":
            raise serializers.ValidationError("스타일 이름은 공백일 수 없습니다.")

        service: Service = self.context.get("service")
        if service.service_style.filter(style_name=style_name).exists():
            raise serializers.ValidationError(
                "해당 style name에 해당하는 Service style이 중복됩니다."
            )

        return attrs

    def create(self, validated_data):
        service_style = ServiceStyle.objects.create(
            market_service=self.context.get("service"), **validated_data
        )
        service_style.save()
        return service_style
