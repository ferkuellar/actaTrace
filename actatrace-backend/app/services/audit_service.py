from typing import Any

from sqlalchemy.orm import Session

from app.models.enums import AuditEventCategory, AuditEventSeverity
from app.models.audit_log import AuditLog
from app.models.user import User
from app.observability.instrumentation import record_audit_metric
from app.observability.metrics import AUDIT_LOG_WRITE_FAILURES_TOTAL
from app.services.state_diff import diff_states


def _infer_category(action: str, entity_type: str) -> AuditEventCategory:
    upper = f"{action} {entity_type}".upper()
    for category in AuditEventCategory:
        if category.value in upper:
            return category
    if "LOGIN" in upper or "AUTH" in upper:
        return AuditEventCategory.AUTH
    return AuditEventCategory.SYSTEM


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        actor_user_id: str | None,
        request_id: str,
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        correlation_id: str | None = None,
        event_category: AuditEventCategory | None = None,
        event_severity: AuditEventSeverity = AuditEventSeverity.INFO,
        changed_fields: dict[str, Any] | None = None,
        geo_location: str | None = None,
        evidence_document_id: str | None = None,
        related_acta_id: str | None = None,
        related_polling_station_id: str | None = None,
        blockchain_anchor_id: str | None = None,
        hash_value: str | None = None,
        metadata_json: dict[str, Any] | None = None,
    ) -> AuditLog:
        actor = self.db.get(User, actor_user_id) if actor_user_id else None
        log = AuditLog(
            actor_user_id=actor_user_id,
            actor_role=actor.role.value if actor else None,
            actor_organization=actor.organization if actor else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
            event_category=event_category or _infer_category(action, entity_type),
            event_severity=event_severity,
            before_state=before_state,
            after_state=after_state,
            changed_fields=changed_fields if changed_fields is not None else diff_states(before_state, after_state),
            ip_address=ip_address,
            user_agent=user_agent,
            geo_location=geo_location,
            evidence_document_id=evidence_document_id,
            related_acta_id=related_acta_id,
            related_polling_station_id=related_polling_station_id,
            blockchain_anchor_id=blockchain_anchor_id,
            hash_value=hash_value,
            metadata_json=metadata_json,
            request_id=request_id,
        )
        try:
            self.db.add(log)
            self.db.flush()
        except Exception:
            AUDIT_LOG_WRITE_FAILURES_TOTAL.labels(action=action).inc()
            raise
        record_audit_metric(action, log.event_category.value, log.event_severity.value)
        return log

    def record_security_event(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        actor_user_id: str | None,
        request_id: str,
        metadata_json: dict[str, Any] | None = None,
    ) -> AuditLog:
        return self.record(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_user_id=actor_user_id,
            request_id=request_id,
            event_category=AuditEventCategory.SECURITY,
            event_severity=AuditEventSeverity.CRITICAL,
            metadata_json=metadata_json,
        )
