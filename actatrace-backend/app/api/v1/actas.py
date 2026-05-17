from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_request_id, require_roles
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.acta_repository import ActaRepository
from app.repositories.custody_repository import CustodyRepository
from app.repositories.prep_repository import PREPRepository
from app.schemas.acta import ActaCreate, ActaRead, ActaRejectRequest, ActaUpdate, HashVerificationResponse
from app.schemas.custody_event import CustodyEventRead
from app.schemas.prep_result import PREPResultRead
from app.services.acta_service import ActaService

router = APIRouter()


@router.get("", response_model=list[ActaRead])
def list_actas(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    return ActaRepository(db).list()


@router.get("/{acta_id}", response_model=ActaRead)
def get_acta(
    acta_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    acta = ActaRepository(db).get(acta_id)
    if not acta:
        raise NotFoundError("Acta not found", code="ACTA_NOT_FOUND")
    return acta


@router.post("", response_model=ActaRead)
def create_acta(
    payload: ActaCreate,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA)),
):
    acta = ActaService(db).create(payload, current_user.id, request_id)
    db.commit()
    db.refresh(acta)
    return acta


@router.patch("/{acta_id}", response_model=ActaRead)
def update_acta(
    acta_id: str,
    payload: ActaUpdate,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR)),
):
    acta = ActaService(db).update(acta_id, payload, current_user.id, request_id)
    db.commit()
    db.refresh(acta)
    return acta


@router.post("/{acta_id}/verify-hash", response_model=HashVerificationResponse)
def verify_hash(
    acta_id: str,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.AUDITOR, UserRole.SUPERVISOR)),
):
    acta = ActaService(db).verify_hash(acta_id, current_user.id, request_id)
    db.commit()
    return HashVerificationResponse(
        acta_id=acta.id,
        document_id=acta.document.id,
        sha256_hash=acta.document.sha256_hash,
        integrity_status=acta.document.integrity_status.value,
    )


@router.post("/{acta_id}/submit-review", response_model=ActaRead)
def submit_review(
    acta_id: str,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR)),
):
    acta = ActaService(db).submit_review(acta_id, current_user.id, request_id)
    db.commit()
    db.refresh(acta)
    return acta


@router.post("/{acta_id}/approve", response_model=ActaRead)
def approve_acta(
    acta_id: str,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR)),
):
    acta = ActaService(db).approve(acta_id, current_user.id, request_id)
    db.commit()
    db.refresh(acta)
    return acta


@router.post("/{acta_id}/reject", response_model=ActaRead)
def reject_acta(
    acta_id: str,
    payload: ActaRejectRequest,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR)),
):
    acta = ActaService(db).reject(acta_id, payload.reason, current_user.id, request_id)
    db.commit()
    db.refresh(acta)
    return acta


@router.get("/{acta_id}/custody-timeline", response_model=list[CustodyEventRead])
def custody_timeline(
    acta_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    return CustodyRepository(db).timeline_for_acta(acta_id)


@router.get("/{acta_id}/prep-results", response_model=list[PREPResultRead])
def prep_results_for_acta(
    acta_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    return PREPRepository(db).list_for_acta(acta_id)
