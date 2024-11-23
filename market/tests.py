from rest_framework.test import APIClient, APITestCase

from market.models import Market
from users.models.reformer import Reformer
from users.models.user import User


class MarketTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            email="test@test.com",
            password="123123",
            phone="01012341234",
            nickname="nickname",
            introduce="hello, django",
            role="reformer",
            is_active=True,
            agreement_terms=True,
        )
        self.reformer = Reformer.objects.create(
            user=self.test_user, reformer_link="www.naver.com", reformer_area="Seoul"
        )
        self.token = self.client.post(
            path=f"/api/user/login",
            data={"email": "test@test.com", "password": "123123"},
        )
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.token.data["access"]
        )

    def test_market_create_simple(self):
        # 단순 마켓 생성 테스트
        response = self.client.post(
            path="/api/market",
            data={
                "market_name": "test market",
                "market_introduce": "Seoul",
                "market_address": "Incheon",
            },
            format="json",
        )

        market_uuid: str = response.data["market_uuid"]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Market.objects.filter(market_uuid=market_uuid).count(), 1)

    def test_market_create_without_reformer(self):
        # 리포머 정보가 없는 사용자가 마켓 생성 시도할 때 막혀야함
        # 1. 일반 사용자 생성
        customer_client = APIClient()
        customer = User.objects.create_user(
            email="customer@test.com",
            password="123123",
            phone="01012341234",
            nickname="nickname",
            introduce="hello, django",
            role="customer",
            is_active=True,
            agreement_terms=True,
        )
        # 2. 로그인 및 인증 수행
        response = self.client.post(
            path="/api/user/login",
            data={"email": customer.email, "password": "123123"},
            format="json",
        )
        customer_client.credentials(
            HTTP_AUTHORIZATION="Bearer " + response.data["access"]
        )
        self.assertEqual(
            User.objects.filter(email=customer.email).first().role, "customer"
        )

        response = customer_client.post(
            path="/api/market",
            data={
                "market_name": "Invalid market",
                "market_introduce": "SHOULD NOT CREATED",
                "market_address": "ABC",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code, 403
        )  # IsReformer 권한 검증 시 막혀야 한다.

    def test_forbid_market_create_more_than_one(self):
        # 이미 마켓이 존재하는데 마켓을 또 생성하는 경우 금지해야함
        response = self.client.post(
            path="/api/market",
            data={
                "market_name": "test market",
                "market_introduce": "Seoul",
                "market_address": "Incheon",
            },
            format="json",
        )  # 마켓 한개 생성 -> 성공
        self.assertEqual(response.data["market_name"], "test market")
        self.assertEqual(
            Market.objects.filter(market_name="test market").first().market_name,
            "test market",
        )

        # 또 생성하는 경우 에러 발생해야함
        invalid_response = self.client.post(
            path="/api/market",
            data={
                "market_name": "invalid market",
                "market_introduce": "13123123",
                "market_address": "invalid",
            },
            format="json",
        )
        self.assertEqual(invalid_response.status_code, 400)

    def test_get_market_info(self):
        # 마켓 정보 생성
        self.client.post(
            path="/api/market",
            data={
                "market_name": "test market",
                "market_introduce": "Seoul",
                "market_address": "Incheon",
            },
            format="json",
        )

        response = self.client.get(path="/api/market", format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["market_name"], "test market")
        self.assertEqual(response.data["market_introduce"], "Seoul")
        self.assertEqual(response.data["market_thumbnail"], None)
        self.assertEqual(response.data["market_address"], "Incheon")
