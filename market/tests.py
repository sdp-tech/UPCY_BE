import os

from rest_framework.test import APIClient, APITestCase
from unittest.mock import patch, MagicMock
from django.test import override_settings

from market.models import Market
from users.models.reformer import Reformer
from users.models.user import User


class MarketTestCase(APITestCase):

    TEST_EMAIL = "test@test.com"
    TEST_CUSTOMER_EMAIL = "customer@test.com"
    TEST_PASSWORD = "123123"
    TEST_MARKET_NAME = "test market"
    TEST_MARKET_INTRODUCE = "asdfasdfasdf"
    TEST_MARKET_ADDRESS = "Seoul"

    @classmethod
    def setUpTestData(cls):
        """일반 사용자 생성 및 인증 설정"""
        cls.customer_client = APIClient()
        cls.customer = User.objects.create_user(
            email=cls.TEST_CUSTOMER_EMAIL,
            password=cls.TEST_PASSWORD,
            phone="01012341234",
            nickname="nickname",
            introduce="hello, django",
            role="customer",
            is_active=True,
            agreement_terms=True,
        )

        # 로그인 및 인증 수행
        response = cls.customer_client.post(
            path="/api/user/login",
            data={"email": cls.customer.email, "password": cls.TEST_PASSWORD},
            format="json",
        )
        cls.customer_client.credentials(
            HTTP_AUTHORIZATION="Bearer " + response.data["access"]
        )

    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
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
                "market_name": self.TEST_MARKET_NAME,
                "market_introduce": self.TEST_MARKET_INTRODUCE,
                "market_address": self.TEST_MARKET_ADDRESS,
            },
            format="json",
        )

        market_uuid: str = response.data["market_uuid"]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Market.objects.filter(market_uuid=market_uuid).count(), 1)

    def test_market_create_without_reformer(self):
        """리포머 권한이 없는 사용자의 마켓 생성 시도 테스트"""
        response = self.customer_client.post(
            path="/api/market",
            data={
                "market_name": "Invalid market",
                "market_introduce": "SHOULD NOT CREATED",
                "market_address": "ABC",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn('detail', response.data)

    def test_forbid_market_create_more_than_one(self):
        # 이미 마켓이 존재하는데 마켓을 또 생성하는 경우 금지해야함
        response = self.client.post(
            path="/api/market",
            data={
                "market_name": self.TEST_MARKET_NAME,
                "market_introduce": self.TEST_MARKET_INTRODUCE,
                "market_address": self.TEST_MARKET_ADDRESS,
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

        # 마켓 정보 획득
        response = self.client.get(path="/api/market", format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["market_name"], "test market")
        self.assertEqual(response.data["market_introduce"], "Seoul")
        self.assertEqual(response.data["market_thumbnail"], None)
        self.assertEqual(response.data["market_address"], "Incheon")

    def test_update_market_info_without_permission(self):
        """권한이 없는 사용자의 마켓 정보 수정 시도 테스트"""
        # 먼저 마켓 생성
        create_response = self.client.post(
            path="/api/market",
            data={
                "market_name": self.TEST_MARKET_NAME,
                "market_introduce": self.TEST_MARKET_INTRODUCE,
                "market_address": self.TEST_MARKET_ADDRESS,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        market_uuid = create_response.data["market_uuid"]

        # 일반 사용자가 마켓 정보 수정 시도
        update_data = {
            "market_name": "Updated Market",
            "market_introduce": "Updated Introduce",
        }
        response = self.customer_client.put(
            f"/api/market/{market_uuid}",
            data=update_data,
            format="json"
        )

        # 권한 검증
        self.assertEqual(response.status_code, 403)
        self.assertIn('detail', response.data)

        # 마켓 정보가 변경되지 않았는지 확인
        market = Market.objects.get(market_uuid=market_uuid)
        self.assertEqual(market.market_name, self.TEST_MARKET_NAME)
        self.assertEqual(market.market_introduce, self.TEST_MARKET_INTRODUCE)


    def test_update_market_info(self):
        # 마켓 정보 수정 시도 테스트
        # 1. 마켓 생성
        create_response = self.client.post(
            path="/api/market",
            data={
                "market_name": self.TEST_MARKET_NAME,
                "market_introduce": self.TEST_MARKET_INTRODUCE,
                "market_address": self.TEST_MARKET_ADDRESS,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        market_uuid = create_response.data["market_uuid"]

        # 2. 마켓 정보 수정
        update_data = {
            "market_name": "Updated Market",
            "market_introduce": "Updated Introduce",
        }
        response = self.client.put(
            f"/api/market/{market_uuid}",
            data=update_data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        # 잘 변경되었는지 확인
        market = Market.objects.get(market_uuid=market_uuid)
        self.assertEqual(market.market_name, update_data["market_name"])
        self.assertEqual(market.market_introduce, update_data["market_introduce"])

    @patch('market.views.market_view.market_crud_view.client')
    def test_delete_market_info(self, mock_boto3_client: MagicMock):
        # 마켓 삭제 시도 테스트

        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3

        # 1. 마켓 생성
        create_response = self.client.post(
            path="/api/market",
            data={
                "market_name": self.TEST_MARKET_NAME,
                "market_introduce": self.TEST_MARKET_INTRODUCE,
                "market_address": self.TEST_MARKET_ADDRESS,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        market_uuid = create_response.data["market_uuid"]

        # 1-2. 마켓 썸네일 이미지 있다고 가정
        market = Market.objects.filter(market_uuid=market_uuid).first()
        market.market_thumbnail = "README.md"
        market.save()

        # 2. 마켓 삭제 요청
        response = self.client.delete(
            f"/api/market/{market_uuid}",
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "market deleted")

        # S3 delete_object 호출 검증
        mock_s3.delete_object.assert_called_once_with(
            Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
            Key="README.md"
        )

        # 마켓 정보가 삭제 되었는지 확인
        self.assertEqual(Market.objects.filter(market_uuid=market_uuid).count(), 0)

    def tearDown(self):
        Market.objects.all().delete()
        Reformer.objects.all().delete()
        User.objects.all().delete()
