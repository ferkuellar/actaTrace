from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models.enums import CustodyEventType
from app.schemas.common import ORMModel


class CustodyEventCreate(BaseModel):
    acta_id: str
    event_type: CustodyEventType
    from_user_id: str | None = None
    to_user_id: str | None = None
    location: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=2000)
    evidence_document_id: str | None = None
    occurred_at: datetime

    @model_validator(mode="after")
    def validate_event_requirements(self) -> "CustodyEventCreate":
        if self.event_type == CustodyEventType.TRANSFERRED and (not self.from_user_id or not self.to_user_id):
            raise ValueError("TRANSFERRED events require from_user_id and to_user_id")
        if self.event_type == CustodyEventType.RECEIVED and not self.to_user_id:
            raise ValueError("RECEIVED events require to_user_id")
        if self.event_type in {CustodyEventType.REJECTED, CustodyEventType.ESCALATED} and not self.notes:
            raise ValueError("REJECTED and ESCALATED events require notes")
        return self


class CustodyEventRead(ORMModel):
    id: str
    acta_id: str
    event_type: CustodyEventType
    from_user_id: str | None = None
    to_user_id: str | None = None
    performed_by: str
    location: str | None = None
    notes: str | None = None
    evidence_document_id: str | None = None
    occurred_at: datetime
    created_at: datetime
