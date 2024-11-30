from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models.reformer import Reformer
from users.models.user import User


class UserTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            email="test@test.com",
            password="123123",
            phone="01012341234",
            nickname="nickname",
            introduce="hello, django",
        )
        self.login_request_data = {"email": "test@test.com", "password": "123123"}

    def test_user_create(self):
        # 정상적인 순서로 회원가입을 진행한 경우
        request_data = {
            "email": "user@test.com",
            "password": "123123",
            "full_name": "hello",
            "agreement_terms": True,
        }
        response = self.client.post(
            path="/api/user/signup", data=request_data, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], "Success")

        created_user = User.objects.get_user_by_email(request_data["email"]).first()
        self.assertEqual(created_user.email, request_data["email"])

    def test_user_create_with_details(self):
        # 선택 정보까지 포함해서 회원가입 테스트
        request_data = {
            "email": "user@test.com",
            "password": "123123",
            "full_name": "hello",
            "agreement_terms": True,
            "nickname": "testuser",
            "introduce": "Hello world",
        }

        response = self.client.post(
            path="/api/user/signup", data=request_data, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], "Success")

        created_user = User.objects.get_user_by_email(request_data["email"]).first()
        self.assertEqual(created_user.email, request_data["email"])
        self.assertEqual(created_user.nickname, request_data["nickname"])
        self.assertEqual(created_user.introduce, request_data["introduce"])

    def test_user_login(self):
        # 존재하지 않는 사용자로 로그인 시 400 에러 발생하는지 확인
        request_data = {"email": "admin@test.com", "password": "123123"}
        response = self.client.post(
            path="/api/user/login", data=request_data, format="json"
        )
        self.assertEqual(response.status_code, 404)

        # 이메일 로그인 시 토큰 발급이 정상적으로 동작하는지 확인
        request_data = {"email": "test@test.com", "password": "123123"}
        response = self.client.post(
            path="/api/user/login", data=request_data, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

        self.assertIn("refresh", response.data)

    def test_user_logout(self):
        # 로그아웃 테스트
        # refresh token이 만료되었는지 확인해야한다.
        # 1. 로그인 수행
        response = self.client.post(
            path=f"/api/user/login", data=self.login_request_data, format="json"
        )
        self.assertEqual(response.status_code, 200)

        # 2. 로그아웃 수행
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])
        refresh_token = response.data["refresh"]
        response = self.client.post(
            path=f"/api/user/logout", data={"refresh": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials()  # 로그아웃 후, client 인증 정보 초기화 (프론트에서 access token 버리는 과정)

        # 3. 인증이 필요한 API 사용 시 에러가 발생해야 한다.
        response = self.client.get(path="/api/user", format="json")
        self.assertEqual(response.status_code, 401)  # 401 Unauthorized

    def test_user_get_data(self):
        # 사용자 정보 GET 테스트
        # 1. 로그인 수행
        response = self.client.post(
            path=f"/api/user/login", data=self.login_request_data, format="json"
        )
        access_token = response.data["access"]
        # 2. 인증정보 없이 요청하면 401 에러 발생
        response = self.client.get(path=f"/api/user", format="json")

        # 3. 사용자 정보 획득 요청
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.get(path="/api/user", format="json")
        self.assertEqual(response.status_code, 200)
        for key, value in response.data.items():
            if key == "profile_image_url":
                continue
            self.assertEqual(response.data[key], getattr(self.test_user, key, None))

    def test_user_update(self):
        # 1. 로그인
        response = self.client.post(
            path=f"/api/user/login", data=self.login_request_data, format="json"
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])

        # 2. 사용자 정보 업데이트 시 금지된 정보를 업데이트 하려고 시도하는 경우
        request_data = {
            "email": "admin@test.com",
            "password": "123123",
        }
        response = self.client.put(path="/api/user", data=request_data, format="json")
        self.assertEqual(response.status_code, 400)

        # 3. 허용된 필드만 업데이트
        before = User.objects.get_user_by_email(
            self.login_request_data["email"]
        ).first()
        request_data = {
            "phone": "123123123",
            "nickname": "updated",
            "introduce": "updated",
        }
        response = self.client.put(path="/api/user", data=request_data, format="json")
        self.assertEqual(response.status_code, 200)

        after = User.objects.get_user_by_email(self.login_request_data["email"]).first()
        for key in ["phone", "nickname", "introduce"]:
            self.assertNotEqual(
                getattr(before, key, None), getattr(after, key, None)
            )  # 기존 내용과 다른지 확인
            self.assertEqual(
                getattr(after, key, None), request_data[key]
            )  # 변경된 사항이 올바르게 반영되었는지 확인

    def test_user_delete(self):
        # 사용자 회원탈퇴 테스트
        # 1. 로그인 하지 않고 요청 시 401 에러 발생해야함
        response = self.client.delete(path="/api/user", format="json")
        self.assertEqual(response.status_code, 401)

        # 2. 로그인
        response = self.client.post(
            path="/api/user/login", data=self.login_request_data, format="json"
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])
        refresh_token: str = response.data["refresh"]

        # 3. 회원 탈퇴
        response = self.client.delete(
            path="/api/user",
            headers={"RefreshToken": refresh_token},
            data={
                "password": self.login_request_data.get("password"),
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        # 4. 디비에 사용자가 남아있는지 확인
        user_count = User.objects.filter(email=self.login_request_data["email"]).count()
        self.assertEqual(user_count, 0)


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
                {"school": "Test School", "major": "Design", "academic_status": "Graduated"},
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
                {"project_name": "Project 1", "description": "Freelance work description"},
            ],
        }

        # 로그인 및 인증 헤더 설정
        self.login_and_set_token()

    def login_and_set_token(self):
        # 로그인 수행 및 인증 헤더 설정
        login_data = {"email": "test@test.com", "password": "123123"}
        response = self.client.post(path="/api/user/login", data=login_data, format="json")
        self.assertEqual(response.status_code, 200, "로그인 실패")
        self.access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

    def test_reformer_create(self):
        before_user = User.objects.get(email="test@test.com")
        self.assertEqual(before_user.role, "customer")
        # 리포머 생성 테스트, 리포머를 생성하는 과정에서 사용자의 역할이 "customer"에서 "reformer"로 변경되는지 확인
        response = self.client.post(path="/api/user/reformer", data=self.reformer_data, format="json")
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
        self.client.post(path="/api/user/reformer", data=self.reformer_data, format="json")

        # 중복 생성 시도를 하면 에러가 발생함
        response = self.client.post(path="/api/user/reformer", data=self.reformer_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.data)

    def test_reformer_create_missing_fields(self):
        # 필요한 필드가 누락된 경우 에러가 발생함
        incomplete_data = {
            "reformer_link": "https://test.com",  # 'reformer_area' 필드 누락
            # "reformer_area": "seoul",
        }
        response = self.client.post(path="/api/user/reformer", data=incomplete_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.data)  # 에러 메시지 확인

    def test_reformer_get(self):
        # 리포머 생성
        self.client.post(path="/api/user/reformer", data=self.reformer_data, format="json")

        # 리포머 데이터 조회
        response = self.client.get(path="/api/user/reformer", format="json")
        self.assertEqual(response.status_code, 200)

        # 데이터 검증
        response_data = response.data
        self.assertEqual(response_data["reformer_link"], self.reformer_data["reformer_link"])
        self.assertEqual(response_data["reformer_area"], self.reformer_data["reformer_area"])

    def test_reformer_update(self):
        # 리포머 생성
        self.client.post(path="/api/user/reformer", data=self.reformer_data, format="json")

        # 리포머 데이터 업데이트
        update_data = {
            "reformer_link": "https://updated-link.com",
            "reformer_area": "seoul gangnam",
        }
        response = self.client.put(path="/api/user/reformer", data=update_data, format="json")
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
            self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.get_access_token(non_reformer_user))

            update_data = {"reformer_link": "https://new-link.com", "reformer_area": "busan"}
            response = self.client.put(path="/api/user/reformer", data=update_data, format="json")

            self.assertEqual(response.status_code, 403)
            self.assertIn("detail", response.data)  # 권한 오류 메시지 확인

    def test_reformer_delete(self):
        # 리포머 생성
        self.client.post(path="/api/user/reformer", data=self.reformer_data, format="json")

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
        self.client.post(path="/api/user/reformer", data=self.reformer_data, format="json")

        # 리포머 삭제
        self.client.delete(path="/api/user/reformer", format="json")

        # 삭제된 리포머가 데이터베이스에서 완전히 삭제되었는지 확인
        reformer_count = Reformer.objects.filter(user=self.test_user).count()
        self.assertEqual(reformer_count, 0)

        # 리포머 재생성 시도
        response = self.client.post(path="/api/user/reformer", data=self.reformer_data, format="json")
        self.assertEqual(response.status_code, 201)

        # 다시 생성된 리포머가 존재하는지 확인
        reformer = Reformer.objects.filter(user=self.test_user).first()
        self.assertIsNotNone(reformer)
        self.assertEqual(reformer.reformer_link, self.reformer_data["reformer_link"])

    def test_reformer_role_check(self):
        # 리포머 생성 후 사용자 역할이 reformer가 되는 것을 다시 확인
        self.client.post(path="/api/user/reformer", data=self.reformer_data, format="json")
        user = User.objects.get(email="test@test.com")
        self.assertEqual(user.role, "reformer")

    def get_access_token(self, user: User):
        login_data = {"email": user.email, "password": "123123"}
        response = self.client.post(path="/api/user/login", data=login_data, format="json")
        return response.data["access"]