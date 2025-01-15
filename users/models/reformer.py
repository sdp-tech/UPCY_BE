import uuid

from django.db import models

from core.models import TimeStampedModel
from users.managers import ReformerManager
from users.models.user import User


def get_reformer_certification_upload_path(instance, filename):
    email_name = instance.reformer.user.email.split("@")[0]
    return f"users/{email_name}/reformer/certifications/{filename}"


def get_portfolio_upload_path(instance, filename):
    email_name = instance.reformer.user.email.split("@")[0]
    return f"users/{email_name}/reformer/portfolio/{filename}"


class Reformer(TimeStampedModel):
    # 리포머 기본 프로필 정보
    # 닉네임, 소개글은 User 테이블에 있는 필드 사용 -> 리포머 생성 요청 시 필요
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="reformer_profile"
    )
    reformer_link = models.TextField(blank=True, null=True)  # 리포머 오픈카톡 링크
    reformer_area = models.CharField(
        max_length=100, blank=True, null=True
    )  # 리포머 활동 지역

    objects = ReformerManager()

    class Meta:
        db_table = "reformer_profile"


class ReformerEducation(TimeStampedModel):
    # 리포머 학력
    reformer = models.ForeignKey(
        "users.Reformer", on_delete=models.CASCADE, related_name="reformer_education"
    )
    education_uuid = models.UUIDField(
        primary_key=True, null=False, unique=True, default=uuid.uuid4
    )
    school = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    academic_status = models.CharField(max_length=100)
    proof_document = models.FileField(
        upload_to=get_reformer_certification_upload_path, null=True, blank=True
    )  # S3에 저장되는 경로

    class Meta:
        db_table = "reformer_education"


class ReformerCertification(TimeStampedModel):
    # 리포머 자격증 내역
    reformer = models.ForeignKey(
        "users.Reformer",
        on_delete=models.CASCADE,
        related_name="reformer_certification",
    )
    certification_uuid = models.UUIDField(
        primary_key=True, null=False, unique=True, default=uuid.uuid4
    )
    name = models.CharField(max_length=100)  # 자격증 명
    issuing_authority = models.CharField(max_length=100)  # 자격증 발급기관 명
    proof_document = models.FileField(
        upload_to=get_reformer_certification_upload_path, null=True, blank=True
    )

    class Meta:
        db_table = "reformer_certification"


class ReformerAwards(TimeStampedModel):
    # 리포머 수상 내역
    reformer = models.ForeignKey(
        "users.Reformer", on_delete=models.CASCADE, related_name="reformer_awards"
    )
    award_uuid = models.UUIDField(
        primary_key=True, null=False, unique=True, default=uuid.uuid4
    )
    competition = models.CharField(max_length=100)  # 공모전 명
    prize = models.CharField(max_length=100)  # 수상 명
    proof_document = models.FileField(
        upload_to=get_reformer_certification_upload_path, null=True, blank=True
    )

    class Meta:
        db_table = "reformer_awards"


class ReformerCareer(TimeStampedModel):
    # 리포머 경력
    reformer = models.ForeignKey(
        "users.Reformer", on_delete=models.CASCADE, related_name="reformer_career"
    )
    career_uuid = models.UUIDField(
        primary_key=True, null=False, unique=True, default=uuid.uuid4
    )
    company_name = models.CharField(max_length=100)  # 근무 회사
    department = models.CharField(max_length=100, null=True, blank=True)  # 근무 부서
    period = models.CharField(
        max_length=30
    )  # 경력 기간 (O년, O개월, .. 이런식으로 입력한다고 하네요)
    proof_document = models.FileField(
        upload_to=get_reformer_certification_upload_path, null=True, blank=True
    )

    class Meta:
        db_table = "reformer_career"


class ReformerFreelancer(TimeStampedModel):
    # 리포머 프리랜서/외주 경력
    reformer = models.ForeignKey(
        "users.Reformer", on_delete=models.CASCADE, related_name="reformer_freelancer"
    )
    freelancer_uuid = models.UUIDField(
        primary_key=True, null=False, unique=True, default=uuid.uuid4
    )
    project_name = models.CharField(max_length=100)  # 프로젝트 이름
    description = (
        models.TextField()
    )  # 프리랜서/외주 수행 시 어떤 일을 했는지에 대한 설명을 저장하는 필드
    proof_document = models.FileField(
        upload_to=get_reformer_certification_upload_path, null=True, blank=True
    )

    class Meta:
        db_table = "reformer_freelancer"
