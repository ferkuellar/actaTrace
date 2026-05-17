from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    success: bool = True
    message: str


class TimestampFields(BaseModel):
    created_at: datetime
    updated_at: datetime | None = None


class IdResponse(BaseModel):
    id: UUID | str
