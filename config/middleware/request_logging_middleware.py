import logging
import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 요청 처리 전에 시작 시간 기록
        start_time = time.time()

        # 요청 정보 로그 출력
        logger.debug(
            f"==============================Request Start=================================="
        )
        logger.debug(f"Request Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.debug(f"Request Path: {request.method} {request.get_full_path()}")
        logger.debug(f"Request Headers: {request.headers}")
        logger.debug(f"Request Method: {request.method}")
        logger.debug(f"Request Body: {request.body.decode('utf-8', errors='replace')}")

        response = self.get_response(request)

        # 요청 처리 시간 계산
        duration = time.time() - start_time

        # 응답 정보 로그 출력
        logger.debug(f"Response Status: {response.status_code}")
        logger.debug(f"Response Headers: {response.headers}")
        logger.debug(
            f"Response Content: {response.content.decode('utf-8', errors='replace')}"
        )
        logger.debug(f"Duration: {duration:.3f}s")
        logger.debug(
            f"==============================Request End=================================="
        )

        return response
