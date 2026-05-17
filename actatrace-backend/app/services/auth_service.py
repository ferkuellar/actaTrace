from sqlalchemy.orm import Session

from app.core.errors import AppError, ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, validate_password_policy, verify_password
from app.models.enums import AuditEventCategory, AuditEventSeverity, UserRole, UserStatus
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register_admin(self, *, full_name: str, email: str, password: str, organization: str) -> User:
        try:
            validate_password_policy(password)
        except ValueError as exc:
            raise AppError(str(exc), code="AUTH_PASSWORD_POLICY_FAILED", status_code=422) from exc
        if self.users.get_by_email(email):
            raise ConflictError("User email already exists", code="USER_EMAIL_EXISTS")
        user = User(
            full_name=full_name,
            email=email.lower(),
            hashed_password=hash_password(password),
            role=UserRole.ADMIN_ELECTORAL,
            organization=organization,
            status=UserStatus.ACTIVE,
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str, request_id: str = "unknown") -> tuple[User, str]:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            AuditService(self.db).record(
                action="AUTH_LOGIN_FAILED",
                entity_type="Auth",
                entity_id=email.lower(),
                actor_user_id=user.id if user else None,
                request_id=request_id,
                event_category=AuditEventCategory.SECURITY,
                event_severity=AuditEventSeverity.WARNING,
                metadata_json={"reason": "invalid_credentials"},
            )
            self.db.commit()
            raise UnauthorizedError("Invalid credentials", code="AUTH_INVALID_CREDENTIALS")
        if user.status != UserStatus.ACTIVE:
            AuditService(self.db).record(
                action="AUTH_LOGIN_FAILED",
                entity_type="User",
                entity_id=user.id,
                actor_user_id=user.id,
                request_id=request_id,
                event_category=AuditEventCategory.SECURITY,
                event_severity=AuditEventSeverity.WARNING,
                metadata_json={"reason": "account_disabled", "status": user.status.value},
            )
            self.db.commit()
            raise UnauthorizedError("User is not active", code="AUTH_ACCOUNT_DISABLED")
        token = create_access_token(
            str(user.id),
            {
                "email": user.email,
                "role": user.role.value,
                "organization": user.organization,
                "status": user.status.value,
            },
        )
        AuditService(self.db).record(
            action="AUTH_LOGIN_SUCCESS",
            entity_type="User",
            entity_id=user.id,
            actor_user_id=user.id,
            request_id=request_id,
            event_category=AuditEventCategory.AUTH,
            event_severity=AuditEventSeverity.INFO,
        )
        return user, token

    def logout(self, user: User, request_id: str) -> None:
        AuditService(self.db).record(
            action="AUTH_LOGOUT",
            entity_type="User",
            entity_id=user.id,
            actor_user_id=user.id,
            request_id=request_id,
            event_category=AuditEventCategory.AUTH,
            event_severity=AuditEventSeverity.INFO,
        )
