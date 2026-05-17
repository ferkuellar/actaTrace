import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import BlockchainAnchorType, BlockchainProviderType, BlockchainVerificationStatus
from app.models.mixins import TimestampMixin


class BlockchainAnchor(TimestampMixin, Base):
    __tablename__ = "blockchain_anchors"
    __table_args__ = (CheckConstraint("length(hash_value) = 64", name="ck_anchor_hash_length"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    anchor_type: Mapped[BlockchainAnchorType] = mapped_column(
        Enum(BlockchainAnchorType, native_enum=False),
        nullable=False,
        index=True,
    )
    hash_value: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    blockchain_network: Mapped[str] = mapped_column(String(120), nullable=False)
    provider: Mapped[BlockchainProviderType] = mapped_column(
        Enum(BlockchainProviderType, native_enum=False),
        nullable=False,
        index=True,
    )
    transaction_hash: Mapped[str | None] = mapped_column(String(200), unique=True, index=True)
    block_number: Mapped[int | None] = mapped_column(nullable=True)
    channel_name: Mapped[str | None] = mapped_column(String(120))
    chaincode_name: Mapped[str | None] = mapped_column(String(120))
    anchored_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_status: Mapped[BlockchainVerificationStatus] = mapped_column(
        Enum(BlockchainVerificationStatus, native_enum=False),
        default=BlockchainVerificationStatus.PENDING,
        nullable=False,
        index=True,
    )
    request_payload: Mapped[dict | None] = mapped_column(JSON)
    response_payload: Mapped[dict | None] = mapped_column(JSON)
    anchored_by: Mapped[str | None] = mapped_column(String(36), index=True)
