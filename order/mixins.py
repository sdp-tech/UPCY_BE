from datetime import date
from typing import Any, Optional, override

from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from core.mixins import QueryParamMixin
from order.models import _OrderStatus


class OrderStatusQueryParamMixin(QueryParamMixin):

    def __init__(self):
        super().__init__()
        self.ALLOWED_FILTER_ARRAY = [choice[0] for choice in _OrderStatus.choices]

    @override
    def apply_filters_and_sorting(
        self, queryset: QuerySet, status: Optional[str]
    ) -> QuerySet:
        if status:
            if status not in self.ALLOWED_FILTER_ARRAY:
                raise ValidationError("Invalid status query parameter")
            return queryset.filter(status=status)
        else:
            return queryset


class OrderQueryParamMinxin(QueryParamMixin):

    def __init__(self):
        super().__init__()
        self.ALLOWED_SORT_FIELDS.update(
            {
                "totalprice": "total_price",
                "-totalprice": "-total_price",
                "date": "created",
                "-date": "-created",
            }
        )
        self.ORDER_STATUS = [
            "accepted",
            "rejected",
            "pending",
            "received",
            "produced",
            "deliver",
            "end",
        ]
        self.TRANSACTION_OPTIONS = ["pickup", "delivery"]

    @override
    def apply_filters_and_sorting(self, queryset: QuerySet, request: Any) -> QuerySet:

        start_date = request.GET.get("start_date", None)  # 2025-01-01 형식
        if start_date:
            queryset = queryset.filter(order_date__gte=date.fromisoformat(start_date))

        end_date = request.GET.get("end_date", None)  # 2025-01-01 형식
        if end_date:
            queryset = queryset.filter(order_date__lte=date.fromisoformat(end_date))

        status = request.GET.get("status")
        if status:
            if status not in self.ORDER_STATUS:
                raise ValueError("Invalid status query parameter")
            queryset = queryset.filter(order_status__status=status)

        transaction = request.GET.get("transaction")
        if transaction:
            if transaction not in self.TRANSACTION_OPTIONS:
                raise ValueError("Invalid status query parameter")
            queryset = queryset.filter(transaction__transaction_option=transaction)

        sort_param = request.GET.get("sort", None)
        if sort_param:
            if sort_param in self.ALLOWED_SORT_FIELDS:
                queryset = queryset.order_by(self.ALLOWED_SORT_FIELDS[sort_param])
            else:
                raise ValueError("Invalid sort query parameter")

        return queryset
