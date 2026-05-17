import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, JSON, ForeignKey, String, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import AuditEventCategory, AuditEventSeverity
from app.models.mixins import utc_now


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(120), index=True)
    actor_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    actor_role: Mapped[str | None] = mapped_column(String(80), index=True)
    actor_organization: Mapped[str | None] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event_category: Mapped[AuditEventCategory] = mapped_column(
        Enum(AuditEventCategory, native_enum=False),
        default=AuditEventCategory.SYSTEM,
        nullable=False,
        index=True,
    )
    event_severity: Mapped[AuditEventSeverity] = mapped_column(
        Enum(AuditEventSeverity, native_enum=False),
        default=AuditEventSeverity.INFO,
        nullable=False,
        index=True,
    )
    before_state: Mapped[dict | None] = mapped_column(JSON)
    after_state: Mapped[dict | None] = mapped_column(JSON)
    changed_fields: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(120))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    geo_location: Mapped[str | None] = mapped_column(String(255))
    evidence_document_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("documents.id"), index=True)
    related_acta_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("actas.id"), index=True)
    related_polling_station_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("polling_stations.id"), index=True)
    blockchain_anchor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("blockchain_anchors.id"), index=True)
    hash_value: Mapped[str | None] = mapped_column(String(64), index=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    actor = relationship("User", foreign_keys=[actor_user_id])


def _reject_audit_mutation(*args, **kwargs) -> None:
    raise ValueError("AuditLog records are append-only and cannot be updated or deleted")


event.listen(AuditLog, "before_update", _reject_audit_mutation)
event.listen(AuditLog, "before_delete", _reject_audit_mutation)
