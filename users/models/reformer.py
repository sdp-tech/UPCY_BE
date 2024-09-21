from django.db import models
from users.models.user import User
from core.models import TimeStampedModel

def get_reformer_certification_upload_path(instance, filename):
    email_name = instance.reformer.user.email.split("@")[0]
    return f"users/{email_name}/reformer/certifications/{filename}"

def get_portfolio_upload_path(instance, filename):
    email_name = instance.reformer.user.email.split("@")[0]
    return f"users/{email_name}/reformer/portfolio/{filename}"

class Reformer(models.Model):
    # 리포머 기본 프로필 정보
    # 닉네임, 소개글은 User 테이블에 있는 필드 사용 -> 리포머 생성 요청 시 필요
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reformer_profile')
    reformer_link = models.TextField(blank=True, null=True) # 리포머 웹페이지 링크 (아마 오픈카톡 링크..?)
    reformer_area = models.CharField(max_length=100, null=True) # 리포머 활동 지역

    class Meta:
        db_table = 'reformer_profile'

class ReformerEducation(models.Model):
    # 리포머 학력
    reformer = models.ForeignKey('users.Reformer', on_delete=models.CASCADE, related_name='reformer_education')
    school = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    academic_status = models.CharField(max_length=100)
    proof_document = models.FileField(upload_to=get_reformer_certification_upload_path, null=True, blank=True)  # S3에 저장되는 경로

    class Meta:
        db_table = 'reformer_education'

class ReformerPortfolio(TimeStampedModel):
    # 리포머의 포트폴리오 자료를 저장하는 테이블
    reformer = models.ForeignKey('users.Reformer', related_name='reformer_portfolio', on_delete=models.CASCADE)

    portfolio = models.FileField(upload_to=get_portfolio_upload_path, null=True, blank=True) # 포트폴리오 파일
    description = models.TextField(null=True, blank=True) # 상세 설명

    class Meta:
        db_table = 'reformer_portfolio'

class ReformerStyle(models.Model):
    # 리포머 작업 스타일
    reformer = models.ForeignKey('users.Reformer', on_delete=models.CASCADE, related_name='reformer_style')
    name = models.CharField(max_length=200)  # 스타일 태그 명

    class Meta:
        db_table = 'reformer_style'

class ReformerMaterial(models.Model):
    # 리포머 주요 사용 재료
    reformer = models.ForeignKey('users.Reformer', on_delete=models.CASCADE, related_name='reformer_material')
    name = models.CharField(max_length=200)  # 특수소재 명

    class Meta:
        db_table = 'reformer_material'

class ReformerCertification(models.Model):
    # 리포머 자격증 내역
    reformer = models.ForeignKey('users.Reformer', on_delete=models.CASCADE, related_name='reformer_certification')
    name = models.CharField(max_length=100)
    issuing_authority = models.CharField(max_length=100)
    issue_date = models.DateField()
    proof_document = models.FileField(upload_to=get_reformer_certification_upload_path, null=True, blank=True)

    class Meta:
        db_table = 'reformer_certification'

class ReformerAwards(models.Model):
    # 리포머 수상 내역
    reformer = models.ForeignKey('users.Reformer', on_delete=models.CASCADE, related_name='reformer_awards')
    name = models.CharField(max_length=100)
    organizer = models.CharField(max_length=100)
    award_date = models.DateField()
    proof_document = models.FileField(upload_to=get_reformer_certification_upload_path, null=True, blank=True)

    class Meta:
        db_table = 'reformer_awards'

class ReformerCareer(models.Model):
    # 리포머 경력
    reformer = models.ForeignKey('users.Reformer', on_delete=models.CASCADE, related_name='reformer_career')
    company_name = models.CharField(max_length=100) # 근무 회사
    department = models.CharField(max_length=100,null=True, blank=True) # 근무 부서
    period = models.CharField(max_length=30) # 경력 기간 (O년, O개월, .. 이런식으로 입력한다고 하네요)
    proof_document = models.FileField(upload_to=get_reformer_certification_upload_path, null=True, blank=True)

    class Meta:
        db_table = 'reformer_career'

class ReformerFreelancer(models.Model):
    # 리포머 프리랜서/외주 경력
    reformer = models.ForeignKey('users.Reformer', on_delete=models.CASCADE, related_name='reformer_freelancer')
    project_name = models.CharField(max_length=100)
    client = models.CharField(max_length=100)
    main_tasks = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    proof_document = models.FileField(upload_to=get_reformer_certification_upload_path, null=True, blank=True)

    class Meta:
        db_table = 'reformer_freelancer'
