from __future__ import annotations

import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.observability.metrics import (
    HTTP_ERRORS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_IN_PROGRESS,
    HTTP_REQUESTS_TOTAL,
    is_public_endpoint,
    normalize_route,
)


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        in_progress_route = normalize_route(request.url.path)
        method = request.method
        HTTP_REQUESTS_IN_PROGRESS.labels(method=method, route=in_progress_route).inc()
        started_at = time.perf_counter()
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            status_code = 500
            raise
        finally:
            elapsed = time.perf_counter() - started_at
            route = getattr(request.scope.get("route"), "path", None) or in_progress_route
            user = getattr(request.state, "user", None)
            role = getattr(getattr(user, "role", None), "value", "anonymous") or "anonymous"
            status_label = str(status_code)
            public = is_public_endpoint(request.url.path)
            HTTP_REQUESTS_TOTAL.labels(method, route, status_label, role, public).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method, route, status_label, role, public).observe(elapsed)
            if status_code >= 400:
                HTTP_ERRORS_TOTAL.labels(method, route, status_label).inc()
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method, route=in_progress_route).dec()
