from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import AlertStatus, AlertType, AuditEventSeverity
from app.schemas.common import ORMModel


class AlertRead(ORMModel):
    id: str
    alert_type: AlertType
    severity: AuditEventSeverity
    status: AlertStatus
    entity_type: str
    entity_id: str
    acta_id: str | None = None
    polling_station_id: str | None = None
    detected_by: str
    description: str
    evidence: dict | None = None
    recommendation: str | None = None
    assigned_to: str | None = None
    resolved_by: str | None = None
    resolution_notes: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None


class AlertAssignRequest(BaseModel):
    assigned_to: str = Field(min_length=1)


class AlertResolveRequest(BaseModel):
    resolution_notes: str = Field(min_length=5, max_length=2000)
    false_positive: bool = False


class AlertEscalateRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)
