import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import DocumentAccessStatus, DocumentIntegrityStatus, DocumentLifecycleStatus
from app.models.mixins import TimestampMixin, utc_now


class Document(TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("file_size > 0", name="ck_documents_file_size_positive"),
        CheckConstraint("length(sha256_hash) = 64", name="ck_documents_sha256_length"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_file_name: Mapped[str | None] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(100), index=True)
    file_size: Mapped[int] = mapped_column(nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    storage_bucket: Mapped[str | None] = mapped_column(String(255))
    storage_key: Mapped[str | None] = mapped_column(String(1000), unique=True, index=True)
    storage_url: Mapped[str | None] = mapped_column(String(2000))
    storage_path: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    uploaded_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    integrity_status: Mapped[DocumentIntegrityStatus] = mapped_column(
        Enum(DocumentIntegrityStatus, native_enum=False),
        default=DocumentIntegrityStatus.PENDING,
        nullable=False,
    )
    access_status: Mapped[DocumentAccessStatus] = mapped_column(
        Enum(DocumentAccessStatus, native_enum=False),
        default=DocumentAccessStatus.PRIVATE,
        nullable=False,
        index=True,
    )
    lifecycle_status: Mapped[DocumentLifecycleStatus] = mapped_column(
        Enum(DocumentLifecycleStatus, native_enum=False),
        default=DocumentLifecycleStatus.UPLOADED,
        nullable=False,
        index=True,
    )
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_integrity_check_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    uploader = relationship("User", back_populates="documents", foreign_keys=[uploaded_by])
    acta = relationship("Acta", back_populates="document", uselist=False)
