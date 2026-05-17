from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_request_id, require_roles
from app.core.database import get_db
from app.models.document import Document
from app.models.enums import DocumentAccessStatus, DocumentIntegrityStatus, UserRole
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import (
    DocumentBlockchainVerificationResponse,
    DocumentDownloadResponse,
    DocumentMetadataCreate,
    DocumentRead,
    IntegrityVerificationResponse,
)
from app.services.document_integrity_service import DocumentIntegrityService
from app.services.document_service import DocumentService
from app.services.document_storage_service import DocumentStorageService

router = APIRouter()


@router.get("", response_model=list[DocumentRead])
def list_documents(
    integrity_status: DocumentIntegrityStatus | None = Query(default=None),
    access_status: DocumentAccessStatus | None = Query(default=None),
    uploaded_by: str | None = Query(default=None),
    acta_id: str | None = Query(default=None),
    polling_station_id: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    query = select(Document)
    if integrity_status:
        query = query.where(Document.integrity_status == integrity_status)
    if access_status:
        query = query.where(Document.access_status == access_status)
    if uploaded_by:
        query = query.where(Document.uploaded_by == uploaded_by)
    if date_from:
        query = query.where(Document.uploaded_at >= date_from)
    if date_to:
        query = query.where(Document.uploaded_at <= date_to)
    if acta_id or polling_station_id:
        from app.models.acta import Acta

        query = query.join(Acta, Acta.document_id == Document.id)
        if acta_id:
            query = query.where(Acta.id == acta_id)
        if polling_station_id:
            query = query.where(Acta.polling_station_id == polling_station_id)
    return list(db.scalars(query.order_by(Document.uploaded_at.desc())).all())


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    document = DocumentStorageService(db).get_metadata(document_id, current_user, request_id)
    db.commit()
    return document


@router.post("/upload-acta", response_model=DocumentRead)
async def upload_acta_document(
    file: UploadFile = File(...),
    acta_id: str = Form(...),
    polling_station_id: str = Form(...),
    document_type: str = Form(...),
    notes: str | None = Form(default=None),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.ADMIN_ELECTORAL, UserRole.CAPTURISTA, UserRole.SUPERVISOR)),
):
    document = await DocumentStorageService(db).upload_acta_document(
        file=file,
        acta_id=acta_id,
        polling_station_id=polling_station_id,
        document_type=document_type,
        notes=notes,
        user=current_user,
        request_id=request_id,
    )
    db.commit()
    db.refresh(document)
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
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.CAPTURISTA, UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    result = DocumentIntegrityService(db, DocumentStorageService(db).storage).verify_integrity(document_id, current_user, request_id)
    db.commit()
    return IntegrityVerificationResponse(**result)


@router.get("/{document_id}/download", response_model=DocumentDownloadResponse)
def download_document(
    document_id: str,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(get_current_user),
):
    service = DocumentStorageService(db)
    download_url = service.create_download_url(document_id, current_user, request_id)
    db.commit()
    from app.core.config import settings

    return DocumentDownloadResponse(
        document_id=document_id,
        download_url=download_url,
        expires_in=settings.document_presigned_url_expire_seconds,
    )


@router.get("/{document_id}/verify-blockchain", response_model=DocumentBlockchainVerificationResponse)
def verify_document_blockchain(
    document_id: str,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.ADMIN_ELECTORAL, UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    result = DocumentIntegrityService(db, DocumentStorageService(db).storage).verify_blockchain(document_id, current_user, request_id)
    db.commit()
    return DocumentBlockchainVerificationResponse(**result)
