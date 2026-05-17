from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import AppError, NotFoundError
from app.models.blockchain_anchor import BlockchainAnchor
from app.models.document import Document
from app.models.enums import DocumentIntegrityStatus
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.blockchain_service import BlockchainService
from app.services.hash_service import HashService
from app.storage.exceptions import StorageObjectMissing, StorageProviderError
from app.storage.provider import StorageProvider


class DocumentIntegrityService:
    def __init__(self, db: Session, storage_provider: StorageProvider) -> None:
        self.db = db
        self.storage = storage_provider
        self.hashes = HashService()
        self.audit = AuditService(db)

    def verify_integrity(self, document_id: str, user: User, request_id: str) -> dict:
        document = self.db.get(Document, document_id)
        if not document:
            raise NotFoundError("Document not found", code="DOCUMENT_NOT_FOUND")
        try:
            content = self.storage.get_file(document.storage_key or document.storage_path)
        except StorageObjectMissing as exc:
            document.integrity_status = DocumentIntegrityStatus.STORAGE_MISSING
            document.last_integrity_check_at = datetime.now(timezone.utc)
            self.audit.record(
                action="DOCUMENT_STORAGE_MISSING",
                entity_type="DOCUMENT",
                entity_id=document.id,
                actor_user_id=user.id,
                request_id=request_id,
            )
            raise NotFoundError("Document object is missing from storage", code="DOCUMENT_STORAGE_MISSING") from exc
        except StorageProviderError as exc:
            raise AppError(exc.message, code=exc.code, status_code=502) from exc

        current_hash = self.hashes.generate_sha256_from_bytes(content)
        database_match = current_hash == document.sha256_hash
        blockchain_hash = None
        blockchain_match = None
        verification = BlockchainService(self.db).verify_hash(document.sha256_hash)
        if verification.exists:
            blockchain_hash = verification.hash_value
            blockchain_match = current_hash == verification.hash_value

        before = {"integrity_status": document.integrity_status.value}
        now = datetime.now(timezone.utc)
        document.last_integrity_check_at = now
        document.verified_at = now if database_match else document.verified_at
        document.integrity_status = DocumentIntegrityStatus.VALID if database_match else DocumentIntegrityStatus.MISMATCH
        action = "DOCUMENT_INTEGRITY_VERIFIED" if database_match else "DOCUMENT_HASH_MISMATCH"
        self.audit.record(
            action=action,
            entity_type="DOCUMENT",
            entity_id=document.id,
            actor_user_id=user.id,
            request_id=request_id,
            before_state=before,
            after_state={
                "database_hash": document.sha256_hash,
                "current_file_hash": current_hash,
                "database_match": database_match,
                "blockchain_match": blockchain_match,
            },
        )
        self.db.flush()
        return {
            "document_id": document.id,
            "database_hash": document.sha256_hash,
            "current_file_hash": current_hash,
            "blockchain_hash": blockchain_hash,
            "database_match": database_match,
            "blockchain_match": blockchain_match,
            "integrity_status": document.integrity_status,
            "verified_at": document.verified_at,
        }

    def verify_blockchain(self, document_id: str, user: User, request_id: str) -> dict:
        document = self.db.get(Document, document_id)
        if not document:
            raise NotFoundError("Document not found", code="DOCUMENT_NOT_FOUND")
        verification = BlockchainService(self.db).verify_hash(document.sha256_hash)
        anchor = self.db.query(BlockchainAnchor).filter(BlockchainAnchor.hash_value == document.sha256_hash).first()
        self.audit.record(
            action="DOCUMENT_BLOCKCHAIN_VERIFIED",
            entity_type="DOCUMENT",
            entity_id=document.id,
            actor_user_id=user.id,
            request_id=request_id,
            after_state={"exists": verification.exists, "anchor_id": anchor.id if anchor else None},
        )
        return {
            "document_id": document.id,
            "database_hash": document.sha256_hash,
            "blockchain_hash": verification.hash_value if verification.exists else None,
            "blockchain_match": verification.exists and verification.hash_value == document.sha256_hash,
            "proof": verification.model_dump(mode="json"),
        }
