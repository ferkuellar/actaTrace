from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ActaStatus
from app.schemas.common import ORMModel


class ActaCreate(BaseModel):
    acta_code: str = Field(pattern=r"^ACTA-[0-9]{4}-[A-Z0-9]{2,5}-[A-Z0-9]{1,10}-[A-Z0-9]{1,10}-[A-Z0-9]{1,10}$")
    polling_station_id: str
    document_id: str | None = None
    election_type: str
    municipality: str
    district: str
    section: str
    expected_total_votes: int | None = Field(default=None, ge=0)


class ActaUpdate(BaseModel):
    document_id: str | None = None
    expected_total_votes: int | None = Field(default=None, ge=0)


class ActaRead(ORMModel):
    id: str
    acta_code: str
    polling_station_id: str
    document_id: str | None = None
    status: ActaStatus
    election_type: str
    municipality: str
    district: str
    section: str
    expected_total_votes: int | None = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    verified_at: datetime | None = None
    blockchain_anchor_id: str | None = None


class ActaRejectRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=1000)


class HashVerificationResponse(BaseModel):
    acta_id: str
    document_id: str
    sha256_hash: str
    integrity_status: str
