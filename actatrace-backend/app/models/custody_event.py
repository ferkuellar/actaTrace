import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import CustodyEventType
from app.models.mixins import utc_now


class CustodyEvent(Base):
    __tablename__ = "custody_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    acta_id: Mapped[str] = mapped_column(String(36), ForeignKey("actas.id"), nullable=False, index=True)
    event_type: Mapped[CustodyEventType] = mapped_column(Enum(CustodyEventType, native_enum=False), nullable=False, index=True)
    from_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    to_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    performed_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(String(2000))
    evidence_document_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("documents.id"))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    acta = relationship("Acta", back_populates="custody_events")
    performer = relationship("User", foreign_keys=[performed_by])
