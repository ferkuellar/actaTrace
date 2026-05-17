import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ActaStatus
from app.models.mixins import TimestampMixin


class Acta(TimestampMixin, Base):
    __tablename__ = "actas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    acta_code: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    polling_station_id: Mapped[str] = mapped_column(String(36), ForeignKey("polling_stations.id"), nullable=False, index=True)
    document_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("documents.id"), unique=True)
    status: Mapped[ActaStatus] = mapped_column(Enum(ActaStatus, native_enum=False), default=ActaStatus.DRAFT, index=True, nullable=False)
    election_type: Mapped[str] = mapped_column(String(80), nullable=False)
    municipality: Mapped[str] = mapped_column(String(120), nullable=False)
    district: Mapped[str] = mapped_column(String(40), nullable=False)
    section: Mapped[str] = mapped_column(String(40), nullable=False)
    expected_total_votes: Mapped[int | None]
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    blockchain_anchor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("blockchain_anchors.id"), unique=True)

    polling_station = relationship("PollingStation", back_populates="actas")
    document = relationship("Document", back_populates="acta", foreign_keys=[document_id])
    creator = relationship("User", back_populates="actas", foreign_keys=[created_by])
    custody_events = relationship("CustodyEvent", back_populates="acta")
    prep_results = relationship("PREPResult", back_populates="acta")
    blockchain_anchor = relationship("BlockchainAnchor", foreign_keys=[blockchain_anchor_id])
