from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_request_id, require_roles
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.custody_repository import CustodyRepository
from app.schemas.custody_event import CustodyEventCreate, CustodyEventRead
from app.services.custody_service import CustodyService

router = APIRouter()


@router.get("", response_model=list[CustodyEventRead])
def list_custody_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    return CustodyRepository(db).list()


@router.get("/{event_id}", response_model=CustodyEventRead)
def get_custody_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    event = CustodyRepository(db).get(event_id)
    if not event:
        raise NotFoundError("Custody event not found", code="CUSTODY_EVENT_NOT_FOUND")
    return event


@router.post("", response_model=CustodyEventRead)
def create_custody_event(
    payload: CustodyEventCreate,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR)),
):
    event = CustodyService(db).create(payload, current_user.id, request_id)
    db.commit()
    db.refresh(event)
    return event
