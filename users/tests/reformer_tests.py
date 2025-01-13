from rest_framework.test import APIClient, APITestCase
from users.models.reformer import Reformer, ReformerEducation, ReformerCertification
from users.models.user import User

class ReformerTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        # 테스트 사용자 생성
        self.test_user = User.objects.create_user(
            email="test@test.com",
            password="123123",
            phone="01012341234",
            full_name="Test User",
            nickname="nickname",
            introduce="hello, django",
        )

        # 리포머 생성에 사용할 데이터
        self.reformer_data = {
            "reformer_link": "https://test.com",
            "reformer_area": "seoul",
            "education": [
                {
                    "school": "Test School",
                    "major": "Design",
                    "academic_status": "Graduated",
                },
            ],
            "certification": [
                {"name": "Certification 1", "issuing_authority": "Authority 1"},
            ],
            "awards": [
                {"competition": "Competition 1", "prize": "First Prize"},
            ],
            "career": [
                {"company_name": "Company 1", "department": "IT", "period": "2 years"},
            ],
            "freelancer": [
                {
                    "project_name": "Project 1",
                    "description": "Freelance work description",
                },
            ],
        }

        # 로그인 및 인증 헤더 설정
        self.login_and_set_token()

    def login_and_set_token(self):
        # 로그인 수행 및 인증 헤더 설정
        login_data = {"email": "test@test.com", "password": "123123"}
        response = self.client.post(
            path="/api/user/login", data=login_data, format="json"
        )
        self.assertEqual(response.status_code, 200, "로그인 실패")
        self.access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

    def test_reformer_create(self):
        before_user = User.objects.get(email="test@test.com")
        self.assertEqual(before_user.role, "customer")
        # 리포머 생성 테스트, 리포머를 생성하는 과정에서 사용자의 역할이 "customer"에서 "reformer"로 변경되는지 확인
        response = self.client.post(
            path="/api/user/reformer", data=self.reformer_data, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], "successfully created")

        after_user = User.objects.get(email="test@test.com")
        self.assertEqual(after_user.role, "reformer")

        # 데이터 검증
        reformer = Reformer.objects.filter(user=self.test_user).first()
        self.assertIsNotNone(reformer)
        self.assertEqual(reformer.reformer_area, self.reformer_data["reformer_area"])

    def test_reformer_duplicate_creation(self):
        # 첫 번째 생성
        self.client.post(
            path="/api/user/reformer", data=self.reformer_data, format="json"
        )

        # 중복 생성 시도를 하면 에러가 발생함
        response = self.client.post(
            path="/api/user/reformer", data=self.reformer_data, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.data)

    def test_reformer_create_missing_fields(self):
        # 필요한 필드가 누락된 경우 에러가 발생함
        incomplete_data = {
            "reformer_link": "https://test.com",  # 'reformer_area' 필드 누락
            # "reformer_area": "seoul",
        }
        response = self.client.post(
            path="/api/user/reformer", data=incomplete_data, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.data)  # 에러 메시지 확인

    def test_reformer_get(self):
        # 리포머 생성
        self.client.post(
            path="/api/user/reformer", data=self.reformer_data, format="json"
        )

        # 리포머 데이터 조회
        response = self.client.get(path="/api/user/reformer", format="json")
        self.assertEqual(response.status_code, 200)

        # 데이터 검증
        response_data = response.data
        self.assertEqual(
            response_data["reformer_link"], self.reformer_data["reformer_link"]
        )
        self.assertEqual(
            response_data["reformer_area"], self.reformer_data["reformer_area"]
        )

    def test_reformer_update(self):
        # 리포머 생성
        self.client.post(
            path="/api/user/reformer", data=self.reformer_data, format="json"
        )

        # 리포머 데이터 업데이트
        update_data = {
            "reformer_link": "https://updated-link.com",
            "reformer_area": "seoul gangnam",
        }
        response = self.client.put(
            path="/api/user/reformer", data=update_data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "successfully updated")

        # 업데이트된 데이터 검증
        reformer = Reformer.objects.get(user=self.test_user)
        self.assertEqual(reformer.reformer_link, update_data["reformer_link"])
        self.assertEqual(reformer.reformer_area, update_data["reformer_area"])

        def test_reformer_update_without_permissions(self):
            # 리포머 역할이 아닌 사용자가 리포머 정보를 업데이트 하려고 할 때 403 오류 발생
            non_reformer_user = User.objects.create_user(
                email="nonreformer@test.com", password="123123"
            )
            self.client.credentials(
                HTTP_AUTHORIZATION="Bearer " + self.get_access_token(non_reformer_user)
            )

            update_data = {
                "reformer_link": "https://new-link.com",
                "reformer_area": "busan",
            }
            response = self.client.put(
                path="/api/user/reformer", data=update_data, format="json"
            )

            self.assertEqual(response.status_code, 403)
            self.assertIn("detail", response.data)  # 권한 오류 메시지 확인

    def test_reformer_delete(self):
        # 리포머 생성
        self.client.post(
            path="/api/user/reformer", data=self.reformer_data, format="json"
        )

        # 리포머 삭제
        response = self.client.delete(path="/api/user/reformer", format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "successfully deleted")

        # 데이터 삭제 확인
        reformer_count = Reformer.objects.filter(user=self.test_user).count()
        self.assertEqual(reformer_count, 0)

    def test_reformer_delete_nonexistent(self):
        # 존재하지 않는 리포머 삭제를 시도하면 에러
        response = self.client.delete(path="/api/user/reformer", format="json")
        self.assertEqual(response.status_code, 404)
        self.assertIn("message", response.data)

    def test_reformer_delete_after_update(self):
        # 리포머 생성
        self.client.post(
            path="/api/user/reformer", data=self.reformer_data, format="json"
        )

        # 리포머 삭제
        self.client.delete(path="/api/user/reformer", format="json")

        # 삭제된 리포머가 데이터베이스에서 완전히 삭제되었는지 확인
        reformer_count = Reformer.objects.filter(user=self.test_user).count()
        self.assertEqual(reformer_count, 0)

        # 리포머 재생성 시도
        response = self.client.post(
            path="/api/user/reformer", data=self.reformer_data, format="json"
        )
        self.assertEqual(response.status_code, 201)

        # 다시 생성된 리포머가 존재하는지 확인
        reformer = Reformer.objects.filter(user=self.test_user).first()
        self.assertIsNotNone(reformer)
        self.assertEqual(reformer.reformer_link, self.reformer_data["reformer_link"])

    def test_reformer_role_check(self):
        # 리포머 생성 후 사용자 역할이 reformer가 되는 것을 다시 확인
        self.client.post(
            path="/api/user/reformer", data=self.reformer_data, format="json"
        )
        user = User.objects.get(email="test@test.com")
        self.assertEqual(user.role, "reformer")

    def test_get_reformer_education_list(self):
        # 1. 리포머 생성
        response = self.client.post(
            path="/api/user/reformer", data=self.reformer_data, format="json"
        )
        reformer_education = ReformerEducation.objects.filter(reformer=self.test_user.reformer_profile).first()
        self.assertEqual(reformer_education.school, self.reformer_data["education"][0]["school"])
        self.assertEqual(response.status_code, 201)

        user: User = User.objects.get_user_by_email(email=self.test_user.email).first()
        self.assertEqual(user.role, "reformer")

        # 2. 학력 정보 조회
        response = self.client.get(
            path="/api/user/reformer/education", format="json"
        )
        self.assertEqual(response.data[0].get("school"), self.reformer_data["education"][0]["school"])
        self.assertEqual(response.status_code, 200)

    def test_get_reformer_cert_list(self):
        # 1. 리포머 생성
        response = self.client.post(
            path="/api/user/reformer", data=self.reformer_data, format="json"
        )
        reformer_certification = ReformerCertification.objects.filter(reformer=self.test_user.reformer_profile).first()
        self.assertEqual(reformer_certification.name, self.reformer_data["certification"][0]["name"])
        self.assertEqual(response.status_code, 201)

        user: User = User.objects.get_user_by_email(email=self.test_user.email).first()
        self.assertEqual(user.role, "reformer")

        # 2. 자격증 정보 조회
        response = self.client.get(
            path="/api/user/reformer/certification", format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0].get("certification_uuid"), str(reformer_certification.certification_uuid))

    def get_access_token(self, user: User):
        login_data = {"email": user.email, "password": "123123"}
        response = self.client.post(
            path="/api/user/login", data=login_data, format="json"
        )
        return response.data["access"]

    def tearDown(self):
        User.objects.all().delete()
        Reformer.objects.all().delete()
        ReformerEducation.objects.all().delete()