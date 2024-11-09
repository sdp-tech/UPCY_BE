from telnetlib import AUTHENTICATION

from rest_framework.test import APIClient, APITestCase

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
            path="/api/user", data={"refresh": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, 200)

        # 4. 디비에 사용자가 남아있는지 확인
        user_count = User.objects.filter(email=self.login_request_data["email"]).count()
        self.assertEqual(user_count, 0)
