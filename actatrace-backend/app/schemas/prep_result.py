from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models.enums import PREPValidationStatus
from app.schemas.common import ORMModel


class PREPResultCreate(BaseModel):
    acta_id: str
    polling_station_id: str
    candidate_results: dict[str, int]
    total_votes: int = Field(ge=0)
    null_votes: int = Field(ge=0)
    valid_votes: int = Field(ge=0)
    captured_at: datetime

    @model_validator(mode="after")
    def validate_totals(self) -> "PREPResultCreate":
        if self.valid_votes + self.null_votes != self.total_votes:
            raise ValueError("total_votes must equal valid_votes + null_votes")
        if sum(self.candidate_results.values()) != self.valid_votes:
            raise ValueError("sum of candidate_results must equal valid_votes")
        return self


class PREPResultRead(ORMModel):
    id: str
    acta_id: str
    polling_station_id: str
    captured_by: str
    candidate_results: dict[str, int]
    total_votes: int
    null_votes: int
    valid_votes: int
    captured_at: datetime
    validation_status: PREPValidationStatus
    mismatch_reason: str | None = None
    created_at: datetime
    updated_at: datetime
