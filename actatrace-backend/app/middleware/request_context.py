import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.started_at = time.perf_counter()
        response = await call_next(request)
        response.headers["x-request-id"] = request.state.request_id
        return response
