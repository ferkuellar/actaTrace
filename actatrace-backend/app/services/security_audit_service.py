from sqlalchemy.orm import Session

from app.models.enums import AuditEventCategory, AuditEventSeverity
from app.services.audit_service import AuditService


class SecurityAuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record_security_event(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        actor_user_id: str | None,
        request_id: str,
        metadata: dict | None = None,
    ):
        return AuditService(self.db).record(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_user_id=actor_user_id,
            request_id=request_id,
            event_category=AuditEventCategory.SECURITY,
            event_severity=AuditEventSeverity.WARNING,
            metadata_json=metadata,
        )
