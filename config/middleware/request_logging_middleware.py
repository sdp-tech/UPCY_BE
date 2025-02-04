import json
import logging
import time

logger = logging.getLogger(__name__)

MAX_BODY_SIZE = 1000  # 최대 로그 출력 크기


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # 요청 본문 크기 확인 및 제한
        request_body: str = ""
        content_length: int = int(request.headers.get("Content-Length", "0"))
        content_type: str = request.headers.get("Content-Type", "").lower()

        if "multipart/form-data" in content_type:
            request_body = "[multipart/form-data] (truncated)"
        else:
            raw_request_body = request.body.decode("utf-8", errors="replace")
            if content_length > MAX_BODY_SIZE:
                request_body = raw_request_body[:MAX_BODY_SIZE] + "... [Truncated]"
            else:
                request_body = raw_request_body

        # 응답 처리
        response = self.get_response(request)
        duration = time.time() - start_time

        # 응답 본문 크기 확인 및 제한
        try:
            response_body = json.loads(response.content.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            response_body = response.content.decode("utf-8", errors="replace")

        if isinstance(response_body, str) and len(response_body) > MAX_BODY_SIZE:
            response_body = response_body[:MAX_BODY_SIZE] + "... [Truncated]"

        # 응답 로그 기록
        logger.info(
            json.dumps(
                {
                    "timestamp": time.time(),
                    "request": {
                        "headers": dict(request.headers),
                        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                        "client_ip": request.META.get("REMOTE_ADDR", ""),
                        "path": request.get_full_path(),
                        "method": request.method,
                        "body": request_body,
                    },
                    "response": {
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "body": response_body,
                        "duration": f"{duration:.3f}s",
                        "response_size": len(response.content),
                    },
                },
                indent=2,
            )
        )

        return response
