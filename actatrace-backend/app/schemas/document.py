from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.enums import DocumentAccessStatus, DocumentIntegrityStatus, DocumentLifecycleStatus
from app.schemas.common import ORMModel

SHA256_PATTERN = r"^[a-f0-9]{64}$"


class DocumentMetadataCreate(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    file_type: str = Field(pattern=r"^(application/pdf|image/jpeg|image/png)$")
    file_size: int = Field(gt=0, le=26_214_400)
    storage_provider: str = Field(min_length=2, max_length=80)
    storage_path: str = Field(min_length=3, max_length=1000)
    sha256_hash: str | None = Field(default=None, pattern=SHA256_PATTERN)
    content_base64: str | None = None

    @field_validator("storage_path")
    @classmethod
    def storage_path_not_public_write(cls, value: str) -> str:
        lowered = value.lower()
        if "public-write" in lowered or "anonymous-write" in lowered or "world-write" in lowered:
            raise ValueError("storage_path cannot be public-write")
        return value


class DocumentVerifyRequest(BaseModel):
    content_base64: str


class DocumentRead(ORMModel):
    id: str
    file_name: str
    original_file_name: str | None = None
    file_type: str
    mime_type: str | None = None
    file_size: int
    storage_provider: str
    storage_bucket: str | None = None
    storage_key: str | None = None
    sha256_hash: str
    uploaded_by: str
    uploaded_at: datetime
    integrity_status: DocumentIntegrityStatus
    access_status: DocumentAccessStatus = DocumentAccessStatus.PRIVATE
    lifecycle_status: DocumentLifecycleStatus = DocumentLifecycleStatus.UPLOADED
    metadata_json: dict | None = None
    verified_at: datetime | None = None
    last_integrity_check_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class IntegrityVerificationResponse(BaseModel):
    document_id: str
    database_hash: str
    current_file_hash: str
    blockchain_hash: str | None = None
    database_match: bool
    blockchain_match: bool | None = None
    integrity_status: DocumentIntegrityStatus
    verified_at: datetime | None = None


class DocumentDownloadResponse(BaseModel):
    document_id: str
    download_url: str
    expires_in: int


class DocumentBlockchainVerificationResponse(BaseModel):
    document_id: str
    database_hash: str
    blockchain_hash: str | None = None
    blockchain_match: bool
    proof: dict
