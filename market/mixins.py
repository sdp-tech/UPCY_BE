from typing import Any, override

from django.db.models import QuerySet

from core.mixins import QueryParamMixin


class ServiceQueryParamMixin(QueryParamMixin):

    def __init__(self):
        super().__init__()
        self.ALLOWED_SORT_FIELDS.update(
            {
                "title": "service_title",  # 서비스 제목 오름차순
                "-title": "-service_title",  # 서비스 제목 내림차순
                "category": "service_category",  # 카테고리 이름 오름차순
                "-category": "-service_category",  # 카테고리 이름 내림차순
                "basic_price": "basic_price",  # 기본 가격 오름차순
                "-basic_price": "-basic_price",  # 기본 가격 내림차순
            }
        )

    @override
    def apply_filters_and_sorting(self, queryset: QuerySet, request: Any) -> QuerySet:

        queryset: QuerySet = super().apply_filters_and_sorting(queryset, request)

        suspended_param: str = request.GET.get("suspended")
        if suspended_param:
            if suspended_param == "true":
                queryset = queryset.filter(suspended=True)  # 중단된 서비스 쿼리셋
            elif suspended_param == "false":
                queryset = queryset.filter(
                    suspended=False
                )  # 현재 제공되는 서비스 쿼리셋
            else:
                raise ValueError("suspended는 true와 false값만 사용할 수 있습니다")

        return queryset
