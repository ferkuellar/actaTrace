from sqlalchemy.orm import Session

from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.enums import UserRole, UserStatus
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register_admin(self, *, full_name: str, email: str, password: str, organization: str) -> User:
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

    def authenticate(self, email: str, password: str) -> tuple[User, str]:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid credentials", code="INVALID_CREDENTIALS")
        if user.status != UserStatus.ACTIVE:
            raise UnauthorizedError("User is not active", code="USER_INACTIVE")
        token = create_access_token(str(user.id), {"role": user.role.value})
        return user, token
