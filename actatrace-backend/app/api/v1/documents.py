from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_request_id, require_roles
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentMetadataCreate, DocumentRead, DocumentVerifyRequest, IntegrityVerificationResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.get("", response_model=list[DocumentRead])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    return DocumentRepository(db).list()


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    document = DocumentRepository(db).get(document_id)
    if not document:
        raise NotFoundError("Document not found", code="DOCUMENT_NOT_FOUND")
    return document


@router.post("/register-metadata", response_model=DocumentRead)
def register_metadata(
    payload: DocumentMetadataCreate,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR)),
):
    document = DocumentService(db).register_metadata(payload, current_user.id, request_id)
    db.commit()
    db.refresh(document)
    return document


@router.post("/{document_id}/verify-integrity", response_model=IntegrityVerificationResponse)
def verify_integrity(
    document_id: str,
    payload: DocumentVerifyRequest,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    document, actual_hash, matches = DocumentService(db).verify_integrity(document_id, payload.content_base64, current_user.id, request_id)
    db.commit()
    return IntegrityVerificationResponse(
        document_id=document.id,
        expected_hash=document.sha256_hash,
        actual_hash=actual_hash,
        matches=matches,
        integrity_status=document.integrity_status,
    )
