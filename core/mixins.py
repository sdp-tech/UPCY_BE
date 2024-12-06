from typing import Any

from django.db.models import QuerySet


class QueryParamMixin:

    def __init__(self):
        self.DEFAULT_SORT = "-created"

        # QueryParamMixin 클래스를 상속받는 쪽에서 __init__ 메서드 오버라이드 하고
        # 만약 정렬 옵션을 추가하는 경우, self.ALLOWED_SORT_FIELDS.update() 사용해서 옵션 추가하시면 됩니다.
        self.ALLOWED_SORT_FIELDS = {
            "created": "created",  # 생성 된 날짜 기준 오름차순
            "-created": "-created",  # 생성 된 날짜 기준 내림차순
            "updated": "updated",  # 업데이트 기준 오름차순
            "-updated": "-updated",  # 업데이트 기준 내림차순
        }

    def apply_filters_and_sorting(self, queryset: QuerySet, request: Any) -> QuerySet:
        """
        QueryParamMixin을 상속받고, 이 메서드를 오버라이드 해서 Sort 코드를 변경하거나
        추가 쿼리 파라미터에 대해 필터링 하는 코드를 추가하시면 됩니다!
        """

        sort_param = request.GET.get("sort")
        if sort_param:
            if sort_param in self.ALLOWED_SORT_FIELDS:
                queryset = queryset.order_by(self.ALLOWED_SORT_FIELDS[sort_param])
            else:
                raise ValueError("정렬 파라미터 값이 올바르지 않습니다.")
        else:
            queryset = queryset.order_by(
                self.ALLOWED_SORT_FIELDS[self.DEFAULT_SORT]
            )  # 따로 안넘어왔다면 기본값으로 created 내림차순 정렬

        return queryset
