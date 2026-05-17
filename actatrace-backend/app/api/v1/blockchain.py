from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_request_id, require_roles
from app.core.database import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.blockchain import BlockchainAnchorRead, PublicBlockchainVerificationRead
from app.services.blockchain_service import BlockchainService

router = APIRouter()


@router.post("/anchor/document/{document_id}", response_model=BlockchainAnchorRead)
def anchor_document_hash(
    document_id: str,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.ADMIN_ELECTORAL, UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    anchor = BlockchainService(db).anchor_document_hash(document_id, current_user.id, request_id)
    db.commit()
    db.refresh(anchor)
    return anchor


@router.post("/anchor/acta/{acta_id}", response_model=BlockchainAnchorRead)
def anchor_acta_document_hash(
    acta_id: str,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.ADMIN_ELECTORAL, UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    anchor = BlockchainService(db).anchor_acta_document_hash(acta_id, current_user.id, request_id)
    db.commit()
    db.refresh(anchor)
    return anchor


@router.post("/anchor/custody-event/{event_id}", response_model=BlockchainAnchorRead)
def anchor_custody_event_hash(
    event_id: str,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.ADMIN_ELECTORAL, UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    anchor = BlockchainService(db).anchor_custody_event_hash(event_id, current_user.id, request_id)
    db.commit()
    db.refresh(anchor)
    return anchor


@router.get("/verify/hash/{hash_value}", response_model=PublicBlockchainVerificationRead)
def verify_hash(hash_value: str, db: Session = Depends(get_db)):
    return BlockchainService(db).verify_hash(hash_value)


@router.get("/anchors/{anchor_id}", response_model=BlockchainAnchorRead)
def get_anchor(
    anchor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN_ELECTORAL, UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    return BlockchainService(db).get_anchor(anchor_id)


@router.get("/anchors/entity/{entity_type}/{entity_id}", response_model=list[BlockchainAnchorRead])
def get_entity_anchors(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN_ELECTORAL, UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    return BlockchainService(db).list_entity_anchors(entity_type, entity_id)
