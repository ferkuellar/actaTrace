from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.rate_limit import InMemoryRateLimiter, RateLimitRule
from app.observability.metrics import HTTP_RATE_LIMITED_TOTAL, PUBLIC_RATE_LIMIT_EXCEEDED_TOTAL


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.limiter = InMemoryRateLimiter()

    async def dispatch(self, request: Request, call_next):
        if not settings.enable_rate_limiting:
            return await call_next(request)
        if request.client and request.client.host == "testclient" and request.headers.get("x-test-rate-limit") != "true":
            return await call_next(request)
        rule = self._match_rule(request)
        if not rule:
            return await call_next(request)
        client = request.client.host if request.client else "unknown"
        if self.limiter.allow(client, rule):
            return await call_next(request)
        HTTP_RATE_LIMITED_TOTAL.labels(route=request.url.path, endpoint_group=rule.name).inc()
        if rule.name.startswith("public"):
            PUBLIC_RATE_LIMIT_EXCEEDED_TOTAL.labels(endpoint_group=rule.name, reason="rate_limit").inc()
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": {
                    "code": "SECURITY_RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    def _match_rule(self, request: Request) -> RateLimitRule | None:
        rules = [
            RateLimitRule("login", "/api/v1/auth/login", settings.rate_limit_login_per_minute, {"POST"}),
            RateLimitRule("public-search", "/api/v1/public/search", settings.rate_limit_public_search_per_minute, {"GET"}),
            RateLimitRule("public-verify", "/api/v1/blockchain/verify/hash", settings.rate_limit_public_verify_per_minute, {"GET"}),
            RateLimitRule("document-download", "/api/v1/documents", settings.rate_limit_document_download_per_minute, {"GET"}),
            RateLimitRule("blockchain-anchor", "/api/v1/blockchain/anchor", settings.rate_limit_blockchain_anchor_per_minute, {"POST"}),
        ]
        for rule in rules:
            if request.url.path.startswith(rule.path_prefix) and (rule.methods is None or request.method in rule.methods):
                return rule
        return None
