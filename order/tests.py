from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.datastructures import MultiValueDict
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from market.models import Market, Service, ServiceMaterial, ServiceOption
from order.models import Order
from users.models.reformer import Reformer
from users.models.user import User


class OrderTestCase(APITestCase):

    def setUp(self):
        super().setUp()
        self.user_client = APIClient()
        self.reformer_client = APIClient()
        self.mock_s3 = patch("storages.backends.s3boto3.S3Boto3Storage.save").start()
        self.mock_s3.return_value = "mocked_file_path/test.jpg"

        self.user = User.objects.create_user(
            email="user@test.com",
            password="asdf1234@@",
            full_name="user",
            nickname="user",
            introduce="hello, django",
            role="customer",
        )

        self.reformer = User.objects.create_user(
            email="reformer@test.com",
            password="asdf1234@@",
            full_name="reformer",
            nickname="reformer",
            introduce="hello, django",
            role="reformer",
        )
        self.reformer_instance = Reformer.objects.create_reformer(
            user=self.reformer,
            reformer_link="https://reformer.com",
            reformer_area="test",
        )

        self.user_client.force_authenticate(user=self.user)
        self.reformer_client.force_authenticate(user=self.reformer)

        self.market = Market.objects.create(
            reformer=self.reformer_instance,
            market_name="test market",
            market_introduce="test market introduce",
            market_address="test market address",
        )

        for _ in range(10):
            self.reformer_client.post(
                path=f"/api/market/{self.market.market_uuid}/service",
                data={
                    "service_title": "reform service",
                    "service_content": "asdfadfgf",
                    "service_category": "category1",
                    "service_style": [
                        {"style_name": "style 1"},
                        {"style_name": "style 2"},
                    ],
                    "service_period": 7,
                    "basic_price": 12345,
                    "max_price": 99999,
                    "service_option": [
                        {
                            "option_name": "option 1",
                            "option_content": "asdfasdfa",
                            "option_price": 123123,
                        },
                        {
                            "option_name": "option 2",
                            "option_content": "asdfasdfa",
                            "option_price": 1256473123,
                        },
                        {
                            "option_name": "option 3",
                            "option_content": "asdfasdfa",
                            "option_price": 12312543,
                        },
                    ],
                    "service_material": [
                        {"material_name": "material 1"},
                        {"material_name": "material 2"},
                    ],
                },
                format="json",
            )

        self.temp_service = Service.objects.all().first()

    @patch(
        "storages.backends.s3boto3.S3Boto3Storage.save",
        return_value="mocked_file_path/test.jpg",
    )
    def test_pickup_order_create_with_basic_user_info(self, _):
        # Given
        # 주문자가 주문 생성 시 전달할 예시 파일 2개 있다고 가정
        # 주문자 정보는 기본 User 객체에서 가져온다 (추가 주문자 정보 X)
        with open("./test_resources/test1.jpg", "rb") as f:
            file_content = f.read()
            file1 = SimpleUploadedFile(
                "test1.jpg",
                file_content,
                content_type="image/jpeg",
            )

        with open("./test_resources/test2.jpg", "rb") as f:
            file_content = f.read()
            file2 = SimpleUploadedFile(
                "test2.jpg",
                file_content,
                content_type="image/jpeg",
            )

        # 주문자가 선택한 재료, 옵션
        selected_materials = ServiceMaterial.objects.filter(
            market_service=self.temp_service
        )
        selected_options = ServiceOption.objects.filter(
            market_service=self.temp_service
        )

        # MultiValueDict를 사용해서 동일한 Key에 여러개의 값이 존재하는 경우 처리 (photo같은거 중복되니까)
        data = MultiValueDict()
        data["transaction_option"] = "pickup"
        data["service_uuid"] = self.temp_service.service_uuid
        data["service_price"] = 50000
        data["option_price"] = 50000
        data["total_price"] = 100000
        data["additional_request"] = "additional request 123"
        data.appendlist(
            "materials",
            [
                str(selected_materials[0].material_uuid),
                str(selected_materials[1].material_uuid),
            ],
        )
        data.appendlist(
            "options",
            [
                str(selected_options[0].option_uuid),
                str(selected_options[1].option_uuid),
            ],
        )
        data.appendlist("images", [file1, file2])

        # When
        # user_client 사용해서 주문 생성
        response = self.user_client.post(
            path=f"/api/orders", data=data, format="multipart"
        )
        print(response.data)

        # Then
        # 제대로 생성되었는지 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("order_uuid", response.data)
        order: Order = Order.objects.filter(
            order_uuid=response.data["order_uuid"]
        ).first()
        self.assertIsNotNone(order)  # Order 객체가 생성되었는지 확인
        self.assertEqual(
            order.order_image.count(), 2
        )  # Order와 연결된 이미지 개수가 2개인지 확인
        self.assertEqual(
            order.order_status.count(), 1
        )  # Order와 연결된 OrderStatus 객체가 생성되었는지 확인
        self.assertIsNotNone(
            order.transaction
        )  # Order와 연결된 Transaction 객체가 생성되었는지 확인
        self.assertEqual(response.data["order_uuid"], str(order.order_uuid))
        self.assertEqual(
            response.data["order_status"],
            order.order_status.order_by("created").first().status,
        )
        self.assertEqual(
            response.data["order_date"], order.order_date.strftime("%Y-%m-%d")
        )

    @patch(
        "storages.backends.s3boto3.S3Boto3Storage.save",
        return_value="mocked_file_path/test.jpg",
    )
    def test_pickup_order_create_with_additional_user_info(self, _):
        # Given
        # 주문자가 주문 생성 시 전달할 예시 파일 2개 있다고 가정
        # 주문자 정보는 기본 User 객체에서 가져온다 (추가 주문자 정보 X)
        with open("./test_resources/test1.jpg", "rb") as f:
            file_content = f.read()
            file1 = SimpleUploadedFile(
                "test1.jpg",
                file_content,
                content_type="image/jpeg",
            )

        with open("./test_resources/test2.jpg", "rb") as f:
            file_content = f.read()
            file2 = SimpleUploadedFile(
                "test2.jpg",
                file_content,
                content_type="image/jpeg",
            )

        # 주문자가 선택한 재료, 옵션
        selected_materials = ServiceMaterial.objects.filter(
            market_service=self.temp_service
        )
        selected_options = ServiceOption.objects.filter(
            market_service=self.temp_service
        )

        # MultiValueDict를 사용해서 동일한 Key에 여러개의 값이 존재하는 경우 처리 (photo같은거 중복되니까)
        data = MultiValueDict()
        data["transaction_option"] = "pickup"
        data["service_uuid"] = self.temp_service.service_uuid
        data["service_price"] = 50000
        data["option_price"] = 50000
        data["total_price"] = 100000
        data["additional_request"] = "additional request 123"
        data["orderer_name"] = "new orderer"
        data["orderer_phone_number"] = "010-1234-5678"
        data["orderer_address"] = "Yeongdeungpo-gu, Seoul"
        data.appendlist(
            "materials",
            [
                str(selected_materials[0].material_uuid),
                str(selected_materials[1].material_uuid),
            ],
        )
        data.appendlist(
            "options",
            [
                str(selected_options[0].option_uuid),
                str(selected_options[1].option_uuid),
            ],
        )
        data.appendlist("images", [file1, file2])

        # When
        # user_client 사용해서 주문 생성
        response = self.user_client.post(
            path=f"/api/orders", data=data, format="multipart"
        )
        print(response.data)

        # Then
        # 제대로 생성되었는지 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("order_uuid", response.data)
        order: Order = Order.objects.filter(
            order_uuid=response.data["order_uuid"]
        ).first()
        self.assertIsNotNone(order)  # Order 객체가 생성되었는지 확인
        self.assertEqual(
            order.order_image.count(), 2
        )  # Order와 연결된 이미지 개수가 2개인지 확인
        self.assertEqual(
            order.order_status.count(), 1
        )  # Order와 연결된 OrderStatus 객체가 생성되었는지 확인
        self.assertIsNotNone(
            order.orderer_information
        )  # Orderer 추가 정보 기입으로 인한 OrdererInformation 객체가 생성되었는지 확인
        self.assertIsNotNone(
            order.transaction
        )  # Order와 연결된 Transaction 객체가 생성되었는지 확인
        self.assertEqual(response.data["order_uuid"], str(order.order_uuid))
        self.assertEqual(
            response.data["order_status"],
            order.order_status.order_by("created").first().status,
        )
        self.assertEqual(
            response.data["order_date"], order.order_date.strftime("%Y-%m-%d")
        )

    @patch(
        "storages.backends.s3boto3.S3Boto3Storage.save",
        return_value="mocked_file_path/test.jpg",
    )
    def test_delivery_order_create_with_basic_user_info(self, _):
        pass

    @patch(
        "storages.backends.s3boto3.S3Boto3Storage.save",
        return_value="mocked_file_path/test.jpg",
    )
    def test_delivery_order_create_with_additional_user_info(self, _):
        pass

    @patch(
        "storages.backends.s3boto3.S3Boto3Storage.save",
        return_value="mocked_file_path/test.jpg",
    )
    def test_get_order_list(self, _):
        # Given
        # 주문 5개 생성
        for itr in range(5):
            with open("./test_resources/test1.jpg", "rb") as f:
                file_content = f.read()
                file1 = SimpleUploadedFile(
                    "test1.jpg",
                    file_content,
                    content_type="image/jpeg",
                )

            with open("./test_resources/test2.jpg", "rb") as f:
                file_content = f.read()
                file2 = SimpleUploadedFile(
                    "test2.jpg",
                    file_content,
                    content_type="image/jpeg",
                )

            # 주문자가 선택한 재료, 옵션
            selected_materials = ServiceMaterial.objects.filter(
                market_service=self.temp_service
            )
            selected_options = ServiceOption.objects.filter(
                market_service=self.temp_service
            )

            data = MultiValueDict()
            data["transaction_option"] = "pickup"
            data["service_uuid"] = self.temp_service.service_uuid
            data["service_price"] = 50000
            data["option_price"] = 50000
            data["total_price"] = 100000
            data["additional_request"] = "additional request 123"
            data["orderer_name"] = "new orderer"
            data["orderer_phone_number"] = "010-1234-5678"
            data["orderer_address"] = "Yeongdeungpo-gu, Seoul"
            data.appendlist(
                "materials",
                [
                    str(selected_materials[0].material_uuid),
                    str(selected_materials[1].material_uuid),
                ],
            )
            data.appendlist(
                "options",
                [
                    str(selected_options[0].option_uuid),
                    str(selected_options[1].option_uuid),
                ],
            )
            data.appendlist("images", [file1, file2])

            if itr == 3:  # orderer 정보가 없는 경우도 테스트
                data.pop("orderer_name")
                data.pop("orderer_phone_number")
                data.pop("orderer_address")

            self.user_client.post(path="/api/orders", data=data, format="multipart")

        self.assertEqual(Order.objects.all().count(), 5)

        # When
        response = self.user_client.get(path="/api/orders", format="json")

        # Then
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("service_uuid", response.data[0])
        self.assertIn("order_uuid", response.data[0])
        self.assertIn("order_date", response.data[0])
        self.assertIn("orderer_information", response.data[0])
        self.assertIn("option_price", response.data[0])
        self.assertIn("service_price", response.data[0])
        self.assertIn("total_price", response.data[0])
        self.assertIn("materials", response.data[0])
        self.assertIn("additional_options", response.data[0])
        self.assertIn("extra_material", response.data[0])
        self.assertIn("additional_request", response.data[0])
        self.assertIn("order_status", response.data[0])
        self.assertIn("transaction", response.data[0])
        self.assertIn("images", response.data[0])
        self.assertIn("created", response.data[0])
        self.assertEqual(len(response.data), 5)

    def tearDown(self):
        patch.stopall()  # 활성화된 Mocking 중단
