from rest_framework import serializers
from users.models import (
    ReformerProfile,
    ReformerEducation,
    Certification,
    Awards,
    Career,
    Freelancer,
    Style,
    Material
)


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['name', 'issuing_authority', 'issue_date', 'proof_document']


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Awards
        fields = ['name', 'organizer', 'award_date', 'proof_document']


class CareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career
        fields = ['company_name', 'department', 'position', 'start_date', 'end_date', 'proof_document']


class FreelancerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freelancer
        fields = ['project_name', 'client', 'main_tasks', 'start_date', 'end_date', 'proof_document']


class ReformerEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReformerEducation
        fields = ['school', 'major', 'academic_status', 'proof_document']


class ReformerProfileSerializer(serializers.ModelSerializer):
    education = ReformerEducationSerializer(many=True)
    certification = CertificationSerializer(many=True)
    awards = AwardSerializer(many=True)
    career = CareerSerializer(many=True)
    freelancer = FreelancerSerializer(many=True)
    style = serializers.CharField(write_only=True)  # 문자열로 입력받음
    material = serializers.CharField(write_only=True)  # 문자열로 입력받음

    class Meta:
        model = ReformerProfile
        fields = [
            'nickname', 'style', 'links', 'market_name', 'market_intro',
            'material', 'education', 'certification', 'awards', 'career', 'freelancer'
        ]

    def validate_style(self, value):
        """콤마로 구분된 문자열을 리스트로 변환하여 스타일 객체로 매핑."""
        style_names = [name.strip() for name in value.split(',') if name.strip()]
        style_objects = [Style.objects.get_or_create(name=name)[0] for name in style_names]
        return style_objects

    def validate_material(self, value):
        """콤마로 구분된 문자열을 리스트로 변환하여 소재 객체로 매핑."""
        material_names = [name.strip() for name in value.split(',') if name.strip()]
        material_objects = [Material.objects.get_or_create(name=name)[0] for name in material_names]
        return material_objects

    def create(self, validated_data):
        style_objects = validated_data.pop('style', [])
        material_objects = validated_data.pop('material', [])

        # 나머지 데이터를 사용하여 프로필 생성
        education_data = validated_data.pop('education', [])
        certification_data = validated_data.pop('certification', [])
        awards_data = validated_data.pop('awards', [])
        career_data = validated_data.pop('career', [])
        freelancer_data = validated_data.pop('freelancer', [])

        # 프로필 생성
        profile = ReformerProfile.objects.create(**validated_data)

        # ManyToMany 필드에 객체 추가
        profile.work_style.set(style_objects)
        profile.special_material.set(material_objects)

        # 교육, 자격증, 수상, 경력, 프리랜서 데이터를 객체로 변환하여 저장
        for edu in education_data:
            ReformerEducation.objects.create(profile=profile, **edu)

        for cert in certification_data:
            Certification.objects.create(profile=profile, **cert)

        for award in awards_data:
            Awards.objects.create(profile=profile, **award)

        for career in career_data:
            Career.objects.create(profile=profile, **career)

        for freelancer in freelancer_data:
            Freelancer.objects.create(profile=profile, **freelancer)

        return profile
