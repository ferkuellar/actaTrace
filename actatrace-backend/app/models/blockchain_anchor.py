import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import BlockchainVerificationStatus
from app.models.mixins import TimestampMixin


class BlockchainAnchor(TimestampMixin, Base):
    __tablename__ = "blockchain_anchors"
    __table_args__ = (CheckConstraint("length(hash_value) = 64", name="ck_anchor_hash_length"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    hash_value: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    blockchain_network: Mapped[str] = mapped_column(String(120), nullable=False)
    transaction_hash: Mapped[str | None] = mapped_column(String(200), unique=True, index=True)
    anchored_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_status: Mapped[BlockchainVerificationStatus] = mapped_column(
        Enum(BlockchainVerificationStatus, native_enum=False),
        default=BlockchainVerificationStatus.PENDING,
        nullable=False,
        index=True,
    )
