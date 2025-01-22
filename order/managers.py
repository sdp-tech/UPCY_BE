from django.db import models

from users.models import User


class OrderManager(models.Manager):

    def get_orders_by_orderer(self, user: User):
        # user 정보를 사용해서 orderer에 관한 order 목록을 가져오기
        return super().get_queryset().filter(orderer=user)

    def get_orders_by_reformer(self, user: User = None):
        # user 정보를 사용해서, reformer가 처리해야할 모든 order 목록을 가져오기
        return super().get_queryset().select_related(
            "service",
            "service__market",
            "service__market__reformer"
        ).filter(service__market__reformer__user=user)
