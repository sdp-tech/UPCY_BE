from rest_framework.test import APIClient, APITestCase

from users.models.reformer import Reformer
from users.models.user import User


class OrderTestCase(APITestCase):

    def setUp(self):
        self.user_client = APIClient()
        self.reformer_client = APIClient()

        user = User.objects.create_user(
            email="user@test.com",
            password="asdf1234@@",
            full_name="user",
            nickname="user",
            introduce="hello, django",
            role="customer",
        )
        reformer = User.objects.create_user(
            email="reformer@test.com",
            password="asdf1234@@",
            full_name="reformer",
            nickname="reformer",
            introduce="hello, django",
            role="reformer",
        )
        Reformer.objects.create()
