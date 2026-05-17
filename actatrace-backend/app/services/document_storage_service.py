import re
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError, ConflictError, ForbiddenError, NotFoundError
from app.models.acta import Acta
from app.models.document import Document
from app.models.enums import DocumentAccessStatus, DocumentIntegrityStatus, DocumentLifecycleStatus, UserRole
from app.models.mixins import utc_now
from app.models.polling_station import PollingStation
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.blockchain_service import BlockchainService
from app.services.hash_service import HashService
from app.storage.exceptions import StorageProviderError
from app.storage.ipfs_provider import IPFSStorageProvider
from app.storage.local_provider import LocalStorageProvider
from app.storage.provider import StorageProvider
from app.storage.s3_provider import S3StorageProvider

ALLOWED_MIME_TYPES = {"application/pdf": ".pdf", "image/jpeg": ".jpg", "image/png": ".png"}
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


class DocumentStorageService:
    def __init__(self, db: Session, storage_provider: StorageProvider | None = None) -> None:
        self.db = db
        self.storage = storage_provider or self._build_storage_provider()
        self.hashes = HashService()
        self.audit = AuditService(db)

    async def upload_acta_document(
        self,
        *,
        file: UploadFile,
        acta_id: str,
        polling_station_id: str,
        document_type: str,
        notes: str | None,
        user: User,
        request_id: str,
    ) -> Document:
        acta = self.db.get(Acta, acta_id)
        if not acta:
            raise NotFoundError("Acta not found", code="ACTA_NOT_FOUND")
        polling_station = self.db.get(PollingStation, polling_station_id)
        if not polling_station:
            raise NotFoundError("Polling station not found", code="POLLING_STATION_NOT_FOUND")
        if acta.polling_station_id != polling_station.id:
            raise ConflictError("Polling station must match acta", code="ACTA_POLLING_STATION_MISMATCH")

        content = await file.read()
        self._validate_file(file, content)
        sha256_hash = self.hashes.generate_sha256_from_bytes(content)
        if self.db.scalar(select(Document).where(Document.sha256_hash == sha256_hash)):
            raise ConflictError("Document hash already exists", code="DOCUMENT_HASH_ALREADY_EXISTS")

        document_id = str(uuid.uuid4())
        extension = ALLOWED_MIME_TYPES[file.content_type]
        object_key = self.generate_object_key(
            election_year=acta.created_at.year,
            state=polling_station.state,
            municipality=polling_station.municipality,
            polling_station_code=polling_station.polling_station_code,
            acta_id=acta.id,
            document_id=document_id,
            extension=extension,
        )

        try:
            upload_result = self.storage.upload_file(content, object_key, file.content_type)
        except StorageProviderError as exc:
            self.audit.record(
                action="DOCUMENT_UPLOAD_FAILED",
                entity_type="DOCUMENT",
                entity_id=document_id,
                actor_user_id=user.id,
                request_id=request_id,
                after_state={"error_code": exc.code, "message": exc.message},
            )
            raise AppError(exc.message, code=exc.code, status_code=502) from exc

        document = Document(
            id=document_id,
            file_name=f"{document_type}{extension}",
            original_file_name=file.filename,
            file_type=file.content_type,
            mime_type=file.content_type,
            file_size=len(content),
            storage_provider=upload_result.provider,
            storage_bucket=upload_result.bucket,
            storage_key=upload_result.object_key,
            storage_path=upload_result.object_key,
            storage_url=upload_result.storage_url,
            sha256_hash=sha256_hash,
            uploaded_by=user.id,
            integrity_status=DocumentIntegrityStatus.VALID,
            access_status=DocumentAccessStatus.PRIVATE,
            lifecycle_status=DocumentLifecycleStatus.STORED,
            metadata_json={"document_type": document_type, "notes": notes, "source": "upload-acta"},
        )
        self.db.add(document)
        acta.document_id = document.id
        self.db.flush()

        self.audit.record(
            action="DOCUMENT_UPLOADED",
            entity_type="DOCUMENT",
            entity_id=document.id,
            actor_user_id=user.id,
            request_id=request_id,
            after_state={"sha256_hash": sha256_hash, "file_size": len(content), "mime_type": file.content_type},
        )
        self.audit.record(
            action="DOCUMENT_HASH_GENERATED",
            entity_type="DOCUMENT",
            entity_id=document.id,
            actor_user_id=user.id,
            request_id=request_id,
            after_state={"sha256_hash": sha256_hash},
        )
        self.audit.record(
            action="DOCUMENT_STORED",
            entity_type="DOCUMENT",
            entity_id=document.id,
            actor_user_id=user.id,
            request_id=request_id,
            after_state={"storage_provider": document.storage_provider, "storage_bucket": document.storage_bucket},
        )

        if settings.enable_auto_blockchain_anchor:
            BlockchainService(self.db).anchor_document_hash(document.id, user.id, request_id)
        return document

    def get_metadata(self, document_id: str, user: User, request_id: str) -> Document:
        document = self._get_document(document_id)
        self.audit.record(
            action="DOCUMENT_RETRIEVED",
            entity_type="DOCUMENT",
            entity_id=document.id,
            actor_user_id=user.id,
            request_id=request_id,
            after_state={"metadata_only": True},
        )
        return document

    def create_download_url(self, document_id: str, user: User, request_id: str) -> str:
        document = self._get_document(document_id)
        if user.role == UserRole.CIUDADANO_PUBLICO and document.access_status != DocumentAccessStatus.PUBLIC_VERIFIABLE:
            self.audit.record(
                action="DOCUMENT_ACCESS_DENIED",
                entity_type="DOCUMENT",
                entity_id=document.id,
                actor_user_id=user.id,
                request_id=request_id,
                after_state={"reason": "document_not_public_verifiable"},
            )
            raise ForbiddenError("Document access denied", code="DOCUMENT_ACCESS_DENIED")
        if not document.storage_key or not self.storage.file_exists(document.storage_key):
            document.integrity_status = DocumentIntegrityStatus.STORAGE_MISSING
            self.audit.record(
                action="DOCUMENT_STORAGE_MISSING",
                entity_type="DOCUMENT",
                entity_id=document.id,
                actor_user_id=user.id,
                request_id=request_id,
            )
            raise NotFoundError("Document object is missing from storage", code="DOCUMENT_STORAGE_MISSING")
        url = self.storage.generate_presigned_url(document.storage_key, settings.document_presigned_url_expire_seconds)
        self.audit.record(
            action="DOCUMENT_RETRIEVED",
            entity_type="DOCUMENT",
            entity_id=document.id,
            actor_user_id=user.id,
            request_id=request_id,
            after_state={"download": True},
        )
        return url

    def generate_object_key(
        self,
        *,
        election_year: int,
        state: str,
        municipality: str,
        polling_station_code: str,
        acta_id: str,
        document_id: str,
        extension: str,
    ) -> str:
        return "/".join(
            [
                "actas",
                str(election_year),
                self._sanitize(state),
                self._sanitize(municipality),
                self._sanitize(polling_station_code),
                self._sanitize(acta_id),
                f"{self._sanitize(document_id)}{extension}",
            ]
        )

    def _validate_file(self, file: UploadFile, content: bytes) -> None:
        if not content:
            raise AppError("Document file is empty", code="DOCUMENT_UPLOAD_FAILED", status_code=400)
        max_bytes = settings.max_document_upload_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise AppError("Document file is too large", code="DOCUMENT_FILE_TOO_LARGE", status_code=413)
        extension = Path(file.filename or "").suffix.lower()
        if file.content_type not in ALLOWED_MIME_TYPES or extension not in ALLOWED_EXTENSIONS:
            raise AppError("Document file type is not allowed", code="DOCUMENT_INVALID_FILE_TYPE", status_code=400)

    def _get_document(self, document_id: str) -> Document:
        document = self.db.get(Document, document_id)
        if not document:
            raise NotFoundError("Document not found", code="DOCUMENT_NOT_FOUND")
        return document

    def _sanitize(self, value: str) -> str:
        sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
        return sanitized[:120] or "unknown"

    def _build_storage_provider(self) -> StorageProvider:
        provider = settings.storage_provider.lower()
        if provider == "local":
            return LocalStorageProvider(settings.local_storage_path)
        if provider in {"s3", "minio"}:
            return S3StorageProvider(
                endpoint_url=settings.s3_endpoint_url,
                access_key=settings.s3_access_key,
                secret_key=settings.s3_secret_key,
                bucket_name=settings.s3_bucket_name,
                region_name=settings.s3_region,
                use_ssl=settings.s3_use_ssl,
            )
        if provider == "ipfs":
            return IPFSStorageProvider()
        raise AppError("Unsupported storage provider", code="DOCUMENT_STORAGE_FAILED", status_code=500)
