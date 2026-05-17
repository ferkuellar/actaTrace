from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_request_id, require_roles
from app.core.database import get_db
from app.core.errors import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.enums import UserRole, UserStatus
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN_ELECTORAL)),
) -> list[User]:
    return UserRepository(db).list()


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN_ELECTORAL)),
) -> User:
    user = UserRepository(db).get(user_id)
    if not user:
        raise NotFoundError("User not found", code="USER_NOT_FOUND")
    return user


@router.post("", response_model=UserRead)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.ADMIN_ELECTORAL)),
) -> User:
    repo = UserRepository(db)
    if repo.get_by_email(payload.email):
        raise ConflictError("User email already exists", code="USER_EMAIL_EXISTS")
    user = User(
        full_name=payload.full_name,
        email=str(payload.email).lower(),
        hashed_password=hash_password(payload.password),
        role=payload.role,
        organization=payload.organization,
        status=payload.status,
    )
    repo.add(user)
    AuditService(db).record(
        action="USER_CREATED",
        entity_type="USER",
        entity_id=user.id,
        actor_user_id=current_user.id,
        request_id=request_id,
        after_state={"email": user.email, "role": user.role.value},
    )
    db.commit()
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.ADMIN_ELECTORAL)),
) -> User:
    user = UserRepository(db).get(user_id)
    if not user:
        raise NotFoundError("User not found", code="USER_NOT_FOUND")
    before = {"role": user.role.value, "status": user.status.value, "organization": user.organization}
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    AuditService(db).record(
        action="USER_UPDATED",
        entity_type="USER",
        entity_id=user.id,
        actor_user_id=current_user.id,
        request_id=request_id,
        before_state=before,
        after_state={"role": user.role.value, "status": user.status.value, "organization": user.organization},
    )
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=UserRead)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.ADMIN_ELECTORAL)),
) -> User:
    user = UserRepository(db).get(user_id)
    if not user:
        raise NotFoundError("User not found", code="USER_NOT_FOUND")
    before = {"status": user.status.value}
    user.status = UserStatus.INACTIVE
    AuditService(db).record(
        action="USER_DEACTIVATED",
        entity_type="USER",
        entity_id=user.id,
        actor_user_id=current_user.id,
        request_id=request_id,
        before_state=before,
        after_state={"status": user.status.value},
    )
    db.commit()
    db.refresh(user)
    return user
