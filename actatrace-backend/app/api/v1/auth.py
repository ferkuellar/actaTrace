from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import AdminRegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register-admin", response_model=TokenResponse)
def register_admin(payload: AdminRegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    service = AuthService(db)
    user = service.register_admin(**payload.model_dump())
    db.commit()
    _, token = service.authenticate(payload.email, payload.password)
    return TokenResponse(access_token=token, user=user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user, token = AuthService(db).authenticate(payload.email, payload.password)
    db.commit()
    return TokenResponse(access_token=token, user=user)
