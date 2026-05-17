from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BlockchainAnchorType, BlockchainProviderType, BlockchainVerificationStatus

SHA256_PATTERN = r"^[a-f0-9]{64}$"


class BlockchainAnchorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entity_type: str
    entity_id: str
    anchor_type: BlockchainAnchorType
    hash_value: str
    blockchain_network: str
    provider: BlockchainProviderType
    transaction_hash: str | None = None
    block_number: int | None = None
    channel_name: str | None = None
    chaincode_name: str | None = None
    verification_status: BlockchainVerificationStatus
    request_payload: dict | None = None
    response_payload: dict | None = None
    anchored_by: str | None = None
    anchored_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class PublicBlockchainVerificationRead(BaseModel):
    exists: bool
    hash_value: str = Field(pattern=SHA256_PATTERN)
    anchor_id: str | None = None
    entity_type: str | None = None
    entity_id: str | None = None
    transaction_id: str | None = None
    anchored_at: datetime | None = None
    proof: dict = Field(default_factory=dict)
