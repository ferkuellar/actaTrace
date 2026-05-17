import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import PREPValidationStatus
from app.models.mixins import TimestampMixin


class PREPResult(TimestampMixin, Base):
    __tablename__ = "prep_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    acta_id: Mapped[str] = mapped_column(String(36), ForeignKey("actas.id"), nullable=False, index=True)
    polling_station_id: Mapped[str] = mapped_column(String(36), ForeignKey("polling_stations.id"), nullable=False, index=True)
    captured_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    candidate_results: Mapped[dict] = mapped_column(JSON, nullable=False)
    total_votes: Mapped[int] = mapped_column(nullable=False)
    null_votes: Mapped[int] = mapped_column(nullable=False)
    valid_votes: Mapped[int] = mapped_column(nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    validation_status: Mapped[PREPValidationStatus] = mapped_column(
        Enum(PREPValidationStatus, native_enum=False),
        default=PREPValidationStatus.PENDING,
        index=True,
        nullable=False,
    )
    mismatch_reason: Mapped[str | None] = mapped_column(String(1000))

    acta = relationship("Acta", back_populates="prep_results")
    polling_station = relationship("PollingStation", back_populates="prep_results")
    capturer = relationship("User", foreign_keys=[captured_by])
