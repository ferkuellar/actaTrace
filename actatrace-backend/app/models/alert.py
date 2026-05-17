import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import AlertStatus, AlertType, AuditEventSeverity
from app.models.mixins import TimestampMixin


class Alert(TimestampMixin, Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType, native_enum=False), nullable=False, index=True)
    severity: Mapped[AuditEventSeverity] = mapped_column(Enum(AuditEventSeverity, native_enum=False), nullable=False, index=True)
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, native_enum=False),
        default=AlertStatus.OPEN,
        nullable=False,
        index=True,
    )
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    acta_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("actas.id"), index=True)
    polling_station_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("polling_stations.id"), index=True)
    detected_by: Mapped[str] = mapped_column(String(120), nullable=False, default="SYSTEM")
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    evidence: Mapped[dict | None] = mapped_column(JSON)
    recommendation: Mapped[str | None] = mapped_column(String(2000))
    assigned_to: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    resolved_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    resolution_notes: Mapped[str | None] = mapped_column(String(2000))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    acta = relationship("Acta", foreign_keys=[acta_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
    resolver = relationship("User", foreign_keys=[resolved_by])
