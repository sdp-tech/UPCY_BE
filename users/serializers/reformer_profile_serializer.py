from rest_framework import serializers
from users.models import (
    ReformerAwards, ReformerCareer, ReformerCertification, ReformerFreelancer,
    ReformerMaterial, ReformerEducation, ReformerProfile, ReformerStyle, User
)


class ReformerCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerCertification
        fields = ['name', 'issuing_authority', 'issue_date']


class ReformerAwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerAwards
        fields = ['name', 'organizer', 'award_date']


class ReformerCareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerCareer
        fields = ['company_name', 'department', 'position', 'start_date', 'end_date']


class ReformerFreelancerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerFreelancer
        fields = ['project_name', 'client', 'main_tasks', 'start_date', 'end_date']


class ReformerEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerEducation
        fields = ['school', 'major', 'academic_status']

class ReformerProfileSerializer(serializers.ModelSerializer):
    # 입력을 위한 필드
    education = ReformerEducationSerializer(many=True, required=False)
    certification = ReformerCertificationSerializer(many=True, required=False)
    awards = ReformerAwardSerializer(many=True, required=False)
    career = ReformerCareerSerializer(many=True, required=False)
    freelancer = ReformerFreelancerSerializer(many=True, required=False)
    style = serializers.CharField(write_only=True)
    material = serializers.CharField(write_only=True)

    # 출력을 위한 필드
    styles = serializers.SerializerMethodField(read_only=True)
    materials = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReformerProfile
        fields = [
            'reformer_link', 'reformer_area', 'style', 'material',
            'styles', 'materials', 'education', 'certification',
            'awards', 'career', 'freelancer',
        ]
        extra_kwargs = {
            'reformer_link': {'required': True},
            'reformer_area': {'required': True},
        }

    def get_styles(self, obj):
        return ','.join([style.name for style in obj.style.all()])

    def get_materials(self, obj):
        return ','.join([material.name for material in obj.material.all()])

    def create(self, validated_data):
        user = self.context.get('request').user
        styles = validated_data.pop('style', '')
        materials = validated_data.pop('material', '')

        education_data = validated_data.pop('education', [])
        certification_data = validated_data.pop('certification', [])
        awards_data = validated_data.pop('awards', [])
        career_data = validated_data.pop('career', [])
        freelancer_data = validated_data.pop('freelancer', [])

        # 리포머 프로필 생성
        profile = ReformerProfile.objects.create(
            user=user,
            reformer_area=validated_data['reformer_area'],
            reformer_link=validated_data['reformer_link'],
        )

        # 스타일 및 재료 처리
        if styles:
            styles_list = styles.split(',')
            for style_name in styles_list:
                ReformerStyle.objects.create(reformer=profile, name=style_name.strip())

        if materials:
            materials_list = materials.split(',')
            for material_name in materials_list:
                ReformerMaterial.objects.create(reformer=profile, name=material_name.strip())

        # 중첩된 데이터 생성
        self.create_nested_data(profile, education_data, certification_data, awards_data, career_data, freelancer_data)

        return profile

    def create_nested_data(self, profile, education_data, certification_data, awards_data, career_data,
                           freelancer_data):
        """Helper function to create nested data."""
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
        styles = validated_data.pop('style', '')
        materials = validated_data.pop('material', '')

        education_data = validated_data.pop('education', [])
        certification_data = validated_data.pop('certification', [])
        awards_data = validated_data.pop('awards', [])
        career_data = validated_data.pop('career', [])
        freelancer_data = validated_data.pop('freelancer', [])

        # 기본 프로필 데이터 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 기존 스타일 및 재료 삭제 후 업데이트
        ReformerStyle.objects.filter(reformer=instance).delete()
        if styles:
            styles_list = styles.split(',')
            for style_name in styles_list:
                ReformerStyle.objects.create(reformer=instance, name=style_name.strip())

        ReformerMaterial.objects.filter(reformer=instance).delete()
        if materials:
            materials_list = materials.split(',')
            for material_name in materials_list:
                ReformerMaterial.objects.create(reformer=instance, name=material_name.strip())

        # 중첩된 데이터 업데이트 처리
        self.update_nested_data(instance, education_data, certification_data, awards_data, career_data, freelancer_data)

        return instance

    def update_nested_data(self, profile, education_data, certification_data, awards_data, career_data,
                           freelancer_data):
        # 교육 업데이트 로직
        ReformerEducation.objects.filter(reformer=profile).delete()
        for edu in education_data:
            ReformerEducation.objects.create(reformer=profile, **edu)

        # 자격증 업데이트 로직
        ReformerCertification.objects.filter(reformer=profile).delete()
        for cert in certification_data:
            ReformerCertification.objects.create(reformer=profile, **cert)

        # 수상 내역 업데이트 로직
        ReformerAwards.objects.filter(reformer=profile).delete()
        for award in awards_data:
            ReformerAwards.objects.create(reformer=profile, **award)

        # 경력 업데이트 로직
        ReformerCareer.objects.filter(reformer=profile).delete()
        for career in career_data:
            ReformerCareer.objects.create(reformer=profile, **career)

        # 프리랜서 경력 업데이트 로직
        ReformerFreelancer.objects.filter(reformer=profile).delete()
        for freelancer in freelancer_data:
            ReformerFreelancer.objects.create(reformer=profile, **freelancer)