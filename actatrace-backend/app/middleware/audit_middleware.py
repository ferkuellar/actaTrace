import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("actatrace.requests")


class StructuredRequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started_at = getattr(request.state, "started_at", time.perf_counter())
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
        user = getattr(request.state, "user", None)
        logger.info(
            "request_completed",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "user_id": getattr(user, "id", None),
                "role": getattr(getattr(user, "role", None), "value", None),
            },
        )
        return response
