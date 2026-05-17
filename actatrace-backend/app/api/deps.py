from collections.abc import Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.models.enums import UserRole, UserStatus
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise UnauthorizedError("Missing bearer token", code="MISSING_TOKEN")
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise UnauthorizedError("Invalid bearer token", code="INVALID_TOKEN") from exc
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid bearer token", code="INVALID_TOKEN")
    user = db.get(User, user_id)
    if not user or user.status != UserStatus.ACTIVE:
        raise UnauthorizedError("User is not active", code="USER_INACTIVE")
    request.state.user = user
    return user


def require_roles(*roles: UserRole) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role == UserRole.ADMIN_ELECTORAL:
            return current_user
        if current_user.role not in roles:
            raise ForbiddenError("Insufficient role permissions", code="RBAC_FORBIDDEN")
        if current_user.role == UserRole.CIUDADANO_PUBLICO:
            raise ForbiddenError("Public users cannot access admin API", code="PUBLIC_USER_FORBIDDEN")
        return current_user

    return dependency
