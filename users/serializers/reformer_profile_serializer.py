from rest_framework import serializers
from users.models.reformer import (
    ReformerAwards, ReformerCareer, ReformerCertification, ReformerFreelancer,
    ReformerEducation, Reformer
)


class ReformerCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerCertification
        fields = ['name', 'issuing_authority']

class ReformerAwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerAwards
        fields = ['competition', 'prize']

class ReformerCareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerCareer
        fields = ['company_name', 'department', 'period']

class ReformerFreelancerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerFreelancer
        fields = ['project_name', 'description']

class ReformerEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerEducation
        fields = ['school', 'major', 'academic_status']

class ReformerProfileSerializer(serializers.Serializer):
    education = ReformerEducationSerializer(many=True, required=False)
    certification = ReformerCertificationSerializer(many=True, required=False)
    awards = ReformerAwardSerializer(many=True, required=False)
    career = ReformerCareerSerializer(many=True, required=False)
    freelancer = ReformerFreelancerSerializer(many=True, required=False)
    reformer_link = serializers.CharField(required=True)
    reformer_area = serializers.CharField(required=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['education'] = ReformerEducationSerializer(instance.reformer_education.all(), many=True).data
        representation['certification'] = ReformerCertificationSerializer(instance.reformer_certification.all(), many=True).data
        representation['awards'] = ReformerAwardSerializer(instance.reformer_awards.all(), many=True).data
        representation['career'] = ReformerCareerSerializer(instance.reformer_career.all(), many=True).data
        representation['freelancer'] = ReformerFreelancerSerializer(instance.reformer_freelancer.all(), many=True).data

        return representation

    def create(self, validated_data):
        user = self.context.get('request').user

        education_data = validated_data.pop('education', [])
        certification_data = validated_data.pop('certification', [])
        awards_data = validated_data.pop('awards', [])
        career_data = validated_data.pop('career', [])
        freelancer_data = validated_data.pop('freelancer', [])

        # 리포머 프로필 생성
        profile = Reformer.objects.create(
            user=user,
            reformer_area=validated_data['reformer_area'],
            reformer_link=validated_data['reformer_link'],
        )

        # 중첩된 데이터 생성
        self.create_nested_data(
            profile=profile,
            education_data=education_data,
            certification_data=certification_data,
            awards_data=awards_data,
            career_data=career_data,
            freelancer_data=freelancer_data
        )

        return profile

    def create_nested_data(self, profile, education_data, certification_data,
                           awards_data, career_data, freelancer_data):

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
        education_data = validated_data.pop('education', [])
        certification_data = validated_data.pop('certification', [])
        awards_data = validated_data.pop('awards', [])
        career_data = validated_data.pop('career', [])
        freelancer_data = validated_data.pop('freelancer', [])

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

    def update_nested_data(self, profile, education_data, certification_data, awards_data, career_data,
                           freelancer_data):

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
