from datetime import datetime

from pydantic import BaseModel, Field

SHA256_PATTERN = r"^[a-f0-9]{64}$"


class DocumentHashAnchorPayload(BaseModel):
    anchor_id: str
    entity_type: str
    entity_id: str
    document_id: str
    sha256_hash: str = Field(pattern=SHA256_PATTERN)
    acta_code: str | None = None
    polling_station_code: str | None = None
    anchored_by: str
    anchored_at: datetime
    source_system: str = "actatrace"
    metadata_hash: str = Field(pattern=SHA256_PATTERN)


class EventHashAnchorPayload(BaseModel):
    anchor_id: str
    entity_type: str
    entity_id: str
    event_type: str
    event_hash: str = Field(pattern=SHA256_PATTERN)
    acta_id: str
    performed_by: str
    occurred_at: datetime
    metadata_hash: str = Field(pattern=SHA256_PATTERN)


class BlockchainAnchorResult(BaseModel):
    provider: str
    blockchain_network: str
    transaction_id: str
    block_number: int | None = None
    anchored_at: datetime
    status: str = "ANCHORED"
    raw_response: dict = Field(default_factory=dict)


class BlockchainVerificationResult(BaseModel):
    exists: bool
    hash_value: str = Field(pattern=SHA256_PATTERN)
    anchor_id: str | None = None
    entity_type: str | None = None
    entity_id: str | None = None
    transaction_id: str | None = None
    anchored_at: datetime | None = None
    proof: dict = Field(default_factory=dict)


class BlockchainTransactionResult(BaseModel):
    transaction_id: str
    found: bool
    block_number: int | None = None
    payload: dict = Field(default_factory=dict)
