from rest_framework import serializers

from users.models.reformer import (Reformer, ReformerAwards, ReformerCareer,
                                   ReformerCertification, ReformerEducation,
                                   ReformerFreelancer)


class ReformerCertificationSerializer(serializers.ModelSerializer):
    certification_uuid = serializers.UUIDField(read_only=True)
    proof_document = serializers.FileField(read_only=True)


    class Meta:
        model = ReformerCertification
        fields = [
            "certification_uuid",
            "name",
            "issuing_authority",
            "proof_document",
        ]
    def create(self, validated_data):
        new_certification = ReformerCertification.objects.create(
            reformer=self.context.get("reformer"), **validated_data
        )
        return new_certification

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class ReformerAwardsSerializer(serializers.ModelSerializer):
    award_uuid = serializers.UUIDField(read_only=True)
    proof_document = serializers.FileField(read_only=True)

    class Meta:
        model = ReformerAwards
        fields = [
            "award_uuid",
            "competition",
            "prize",
            "proof_document",
        ]

    def create(self, validated_data):
        new_awards = ReformerAwards.objects.create(
            reformer=self.context.get("reformer"), **validated_data
        )
        return new_awards

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

class ReformerCareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerCareer
        fields = ["company_name", "department", "period"]


class ReformerFreelancerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerFreelancer
        fields = ["project_name", "description"]


class ReformerEducationSerializer(serializers.ModelSerializer):
    education_uuid = serializers.UUIDField(read_only=True)
    proof_document = serializers.FileField(read_only=True)

    class Meta:
        model = ReformerEducation
        fields = [
            "education_uuid",
            "school",
            "major",
            "academic_status",
            "proof_document",
        ]

    def create(self, validated_data):
        new_education = ReformerEducation.objects.create(
            reformer=self.context.get("reformer"), **validated_data
        )
        return new_education

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class ReformerProfileSerializer(serializers.Serializer):
    nickname = serializers.SerializerMethodField()
    education = ReformerEducationSerializer(many=True, required=False)
    certification = ReformerCertificationSerializer(many=True, required=False)
    awards = ReformerAwardsSerializer(many=True, required=False)
    career = ReformerCareerSerializer(many=True, required=False)
    freelancer = ReformerFreelancerSerializer(many=True, required=False)
    reformer_link = serializers.CharField(required=True)
    reformer_area = serializers.CharField(required=True)

    def get_nickname(self, obj):
        # Reformer에서 user 객체에 존재하는 nickname 가져오기 위한 함수
        # SerializerMethodField가 사용한다.
        return obj.user.nickname

    def validate(self, attrs):
        # 1. 요청한 user가 이미 reformer 프로필을 생성했는가?
        request = self.context.get('request')
        if Reformer.objects.filter(user=request.user).exists():
            raise serializers.ValidationError(
                "해당 사용자는 이미 Reformer 프로필을 등록하였습니다."
            )

        # 2. reformer link가 http 또는 https로 시작하는가?
        if "reformer_link" in attrs:
            if not (attrs["reformer_link"].startswith("http://") or attrs["reformer_link"].startswith("https://")):
                raise serializers.ValidationError("Reformer link는 http 또는 https로 시작해야 합니다.")

        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["education"] = ReformerEducationSerializer(
            instance.reformer_education.all(), many=True
        ).data
        representation["certification"] = ReformerCertificationSerializer(
            instance.reformer_certification.all(), many=True
        ).data
        representation["awards"] = ReformerAwardsSerializer(
            instance.reformer_awards.all(), many=True
        ).data
        representation["career"] = ReformerCareerSerializer(
            instance.reformer_career.all(), many=True
        ).data
        representation["freelancer"] = ReformerFreelancerSerializer(
            instance.reformer_freelancer.all(), many=True
        ).data

        return representation

    def create(self, validated_data):
        user = self.context.get("request").user

        education_data = validated_data.pop("education", [])
        certification_data = validated_data.pop("certification", [])
        awards_data = validated_data.pop("awards", [])
        career_data = validated_data.pop("career", [])
        freelancer_data = validated_data.pop("freelancer", [])

        # 리포머 프로필 생성
        profile = Reformer.objects.create(
            user=user,
            reformer_area=validated_data["reformer_area"],
            reformer_link=validated_data["reformer_link"],
        )

        # 중첩된 데이터 생성
        self.create_nested_data(
            profile=profile,
            education_data=education_data,
            certification_data=certification_data,
            awards_data=awards_data,
            career_data=career_data,
            freelancer_data=freelancer_data,
        )

        return profile

    def create_nested_data(
        self,
        profile,
        education_data,
        certification_data,
        awards_data,
        career_data,
        freelancer_data,
    ):

        for edu in education_data:
            ReformerEducation.objects.create(reformer=profile, **edu)

        for cert in certification_data:
            ReformerCertification.objects.create(reformer=profile, **cert)

        for award in awards_data:
            ReformerAwards.objects.create(reformer=profile, **award)

        for career in career_data:
            ReformerCareer.objects.create(reformer=profile, **career)

        for freelancer in freelancer_data:
            ReformerFreelancer.objects.create(reformer=profile, **freelancer)

    def update(self, instance, validated_data):
        education_data = validated_data.pop("education", [])
        certification_data = validated_data.pop("certification", [])
        awards_data = validated_data.pop("awards", [])
        career_data = validated_data.pop("career", [])
        freelancer_data = validated_data.pop("freelancer", [])

        # 기본 프로필 데이터 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 중첩된 데이터 업데이트 처리
        self.update_nested_data(
            profile=instance,
            education_data=education_data,
            certification_data=certification_data,
            awards_data=awards_data,
            career_data=career_data,
            freelancer_data=freelancer_data,
        )

        return instance

    def update_nested_data(
        self,
        profile,
        education_data,
        certification_data,
        awards_data,
        career_data,
        freelancer_data,
    ):

        ReformerEducation.objects.filter(reformer=profile).delete()
        for edu in education_data:
            ReformerEducation.objects.create(reformer=profile, **edu)

        ReformerCertification.objects.filter(reformer=profile).delete()
        for cert in certification_data:
            ReformerCertification.objects.create(reformer=profile, **cert)

        ReformerAwards.objects.filter(reformer=profile).delete()
        for award in awards_data:
            ReformerAwards.objects.create(reformer=profile, **award)

        ReformerCareer.objects.filter(reformer=profile).delete()
        for career in career_data:
            ReformerCareer.objects.create(reformer=profile, **career)

        ReformerFreelancer.objects.filter(reformer=profile).delete()
        for freelancer in freelancer_data:
            ReformerFreelancer.objects.create(reformer=profile, **freelancer)
