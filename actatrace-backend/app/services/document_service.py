from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.document import Document
from app.models.enums import DocumentIntegrityStatus
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentMetadataCreate
from app.services.audit_service import AuditService
from app.services.hash_service import HashService


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.documents = DocumentRepository(db)
        self.hashes = HashService()
        self.audit = AuditService(db)

    def register_metadata(self, payload: DocumentMetadataCreate, user_id: str, request_id: str) -> Document:
        sha256_hash = payload.sha256_hash
        if payload.content_base64:
            sha256_hash = self.hashes.generate_sha256_from_bytes(self.hashes.decode_base64(payload.content_base64))
        if not sha256_hash:
            raise ConflictError("Either sha256_hash or content_base64 is required", code="DOCUMENT_HASH_REQUIRED")
        if self.documents.get_by_hash(sha256_hash):
            raise ConflictError("Document hash already exists", code="DOCUMENT_HASH_EXISTS")
        document = Document(
            file_name=payload.file_name,
            file_type=payload.file_type,
            file_size=payload.file_size,
            storage_provider=payload.storage_provider,
            storage_path=payload.storage_path,
            sha256_hash=sha256_hash,
            uploaded_by=user_id,
            integrity_status=DocumentIntegrityStatus.VALID,
        )
        self.documents.add(document)
        self.audit.record(
            action="DOCUMENT_REGISTERED",
            entity_type="DOCUMENT",
            entity_id=document.id,
            actor_user_id=user_id,
            request_id=request_id,
            after_state={"sha256_hash": document.sha256_hash, "storage_path": document.storage_path},
        )
        return document

    def verify_integrity(self, document_id: str, content_base64: str, user_id: str, request_id: str) -> tuple[Document, str, bool]:
        document = self.documents.get(document_id)
        if not document:
            raise NotFoundError("Document not found", code="DOCUMENT_NOT_FOUND")
        content = self.hashes.decode_base64(content_base64)
        actual_hash = self.hashes.generate_sha256_from_bytes(content)
        matches = actual_hash == document.sha256_hash
        previous = document.integrity_status.value
        document.integrity_status = DocumentIntegrityStatus.VALID if matches else DocumentIntegrityStatus.MISMATCH
        self.audit.record(
            action="DOCUMENT_INTEGRITY_VERIFIED" if matches else "DOCUMENT_HASH_MISMATCH",
            entity_type="DOCUMENT",
            entity_id=document.id,
            actor_user_id=user_id,
            request_id=request_id,
            before_state={"integrity_status": previous},
            after_state={"integrity_status": document.integrity_status.value, "actual_hash": actual_hash},
        )
        self.db.flush()
        return document, actual_hash, matches
