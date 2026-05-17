from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_request_id, require_roles
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.prep_repository import PREPRepository
from app.schemas.prep_result import PREPResultCreate, PREPResultRead
from app.services.prep_service import PREPService

router = APIRouter()


@router.get("", response_model=list[PREPResultRead])
def list_prep_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    return PREPRepository(db).list()


@router.get("/{prep_result_id}", response_model=PREPResultRead)
def get_prep_result(
    prep_result_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    result = PREPRepository(db).get(prep_result_id)
    if not result:
        raise NotFoundError("PREP result not found", code="PREP_RESULT_NOT_FOUND")
    return result


@router.post("", response_model=PREPResultRead)
def create_prep_result(
    payload: PREPResultCreate,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA)),
):
    result = PREPService(db).create(payload, current_user.id, request_id)
    db.commit()
    db.refresh(result)
    return result


@router.post("/{prep_result_id}/validate", response_model=PREPResultRead)
def validate_prep_result(
    prep_result_id: str,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    result = PREPService(db).validate(prep_result_id, current_user.id, request_id)
    db.commit()
    db.refresh(result)
    return result
