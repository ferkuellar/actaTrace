import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import DocumentIntegrityStatus
from app.models.mixins import TimestampMixin, utc_now


class Document(TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("file_size > 0", name="ck_documents_file_size_positive"),
        CheckConstraint("length(sha256_hash) = 64", name="ck_documents_sha256_length"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(80), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    uploaded_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    integrity_status: Mapped[DocumentIntegrityStatus] = mapped_column(
        Enum(DocumentIntegrityStatus, native_enum=False),
        default=DocumentIntegrityStatus.PENDING,
        nullable=False,
    )

    uploader = relationship("User", back_populates="documents", foreign_keys=[uploaded_by])
    acta = relationship("Acta", back_populates="document", uselist=False)
