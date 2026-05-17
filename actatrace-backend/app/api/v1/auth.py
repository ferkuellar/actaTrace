from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_request_id
from app.core.database import get_db
from app.schemas.auth import AdminRegisterRequest, LoginRequest, LogoutResponse, TokenResponse
from app.schemas.user import UserRead
from app.models.user import User
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register-admin", response_model=TokenResponse)
def register_admin(
    payload: AdminRegisterRequest,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> TokenResponse:
    service = AuthService(db)
    user = service.register_admin(**payload.model_dump())
    db.commit()
    _, token = service.authenticate(payload.email, payload.password, request_id)
    return TokenResponse(access_token=token, user=user)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> TokenResponse:
    user, token = AuthService(db).authenticate(payload.email, payload.password, request_id)
    db.commit()
    return TokenResponse(access_token=token, user=user)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(get_current_user),
) -> LogoutResponse:
    AuthService(db).logout(current_user, request_id)
    db.commit()
    return LogoutResponse()


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
