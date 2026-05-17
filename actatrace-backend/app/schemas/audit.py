from datetime import datetime

from app.models.enums import AuditEventCategory, AuditEventSeverity
from app.schemas.common import ORMModel


class AuditLogRead(ORMModel):
    id: str
    request_id: str
    correlation_id: str | None = None
    actor_user_id: str | None = None
    actor_role: str | None = None
    actor_organization: str | None = None
    action: str
    entity_type: str
    entity_id: str
    event_category: AuditEventCategory
    event_severity: AuditEventSeverity
    before_state: dict | None = None
    after_state: dict | None = None
    changed_fields: dict | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    geo_location: str | None = None
    evidence_document_id: str | None = None
    related_acta_id: str | None = None
    related_polling_station_id: str | None = None
    blockchain_anchor_id: str | None = None
    hash_value: str | None = None
    metadata_json: dict | None = None
    created_at: datetime


class TraceabilityEventRead(ORMModel):
    id: str
    event_type: str
    event_category: str
    severity: str
    timestamp: datetime
    entity_type: str
    entity_id: str
    actor: dict | None = None
    location: str | None = None
    before_state: dict | None = None
    after_state: dict | None = None
    evidence: dict | None = None
    verification_status: str | None = None


class ForensicReportRead(ORMModel):
    acta: dict
    document: dict | None = None
    custody_timeline: list[dict]
    prep_results: list[dict]
    hash_verification_status: dict
    blockchain_anchor_status: dict
    inconsistencies: list[dict]
    alerts: list[dict]
    audit_summary: dict
    generated_at: datetime
