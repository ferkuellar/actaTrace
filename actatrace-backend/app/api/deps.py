from collections.abc import Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.models.enums import AuditEventCategory, AuditEventSeverity, UserRole, UserStatus
from app.models.user import User
from app.observability.metrics import AUTH_FORBIDDEN_TOTAL, AUTH_UNAUTHORIZED_TOTAL, endpoint_group
from app.services.audit_service import AuditService

bearer_scheme = HTTPBearer(auto_error=False)


def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _record_security_event(
    db: Session,
    request: Request,
    *,
    action: str,
    code: str,
    actor_user_id: str | None = None,
    entity_type: str = "Auth",
    entity_id: str = "unknown",
) -> None:
    if action == "AUTH_UNAUTHORIZED":
        AUTH_UNAUTHORIZED_TOTAL.labels(role="anonymous", endpoint_group=endpoint_group(request.url.path), reason=code).inc()
    if action == "AUTH_FORBIDDEN":
        role = "unknown"
        if actor_user_id:
            actor = db.get(User, actor_user_id)
            role = actor.role.value if actor else "unknown"
        AUTH_FORBIDDEN_TOTAL.labels(role=role, endpoint_group=endpoint_group(request.url.path), reason=code).inc()
    AuditService(db).record(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        request_id=get_request_id(request),
        event_category=AuditEventCategory.SECURITY,
        event_severity=AuditEventSeverity.WARNING,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        metadata_json={"code": code, "path": request.url.path, "method": request.method},
    )
    db.commit()


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        _record_security_event(db, request, action="AUTH_UNAUTHORIZED", code="MISSING_TOKEN")
        raise UnauthorizedError("Missing bearer token", code="MISSING_TOKEN")
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        _record_security_event(db, request, action="AUTH_UNAUTHORIZED", code="AUTH_TOKEN_INVALID")
        raise UnauthorizedError("Invalid bearer token", code="AUTH_TOKEN_INVALID") from exc
    user_id = payload.get("sub")
    if not user_id:
        _record_security_event(db, request, action="AUTH_UNAUTHORIZED", code="AUTH_TOKEN_INVALID")
        raise UnauthorizedError("Invalid bearer token", code="AUTH_TOKEN_INVALID")
    user = db.get(User, user_id)
    if not user or user.status != UserStatus.ACTIVE:
        _record_security_event(db, request, action="AUTH_UNAUTHORIZED", code="AUTH_ACCOUNT_DISABLED", actor_user_id=user_id)
        raise UnauthorizedError("User is not active", code="AUTH_ACCOUNT_DISABLED")
    request.state.user = user
    return user


def require_roles(*roles: UserRole) -> Callable:
    def dependency(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role == UserRole.ADMIN_ELECTORAL:
            return current_user
        if current_user.role not in roles:
            _record_security_event(
                db,
                request,
                action="AUTH_FORBIDDEN",
                code="RBAC_FORBIDDEN",
                actor_user_id=current_user.id,
                entity_type="User",
                entity_id=current_user.id,
            )
            raise ForbiddenError("Insufficient role permissions", code="RBAC_FORBIDDEN")
        if current_user.role == UserRole.CIUDADANO_PUBLICO:
            _record_security_event(
                db,
                request,
                action="AUTH_FORBIDDEN",
                code="PUBLIC_USER_FORBIDDEN",
                actor_user_id=current_user.id,
                entity_type="User",
                entity_id=current_user.id,
            )
            raise ForbiddenError("Public users cannot access admin API", code="PUBLIC_USER_FORBIDDEN")
        return current_user

    return dependency
