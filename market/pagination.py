from rest_framework.pagination import LimitOffsetPagination


class ServiceListPagination(LimitOffsetPagination):
    """
    페이지네이션 설정 클래스.
    default_limit : GET 요청 시 limit과 offset 파라미터를 지정하지 않았을 때의 기본값
    max_limit : GET 요청 시 최대로 가져올 수 있는 데이터의 개수 제한
    """
    default_limit = 10
    max_limit = 100
