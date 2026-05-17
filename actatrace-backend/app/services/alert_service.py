from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.alert import Alert
from app.models.enums import AlertStatus, AlertType, AuditEventCategory, AuditEventSeverity
from app.models.mixins import utc_now
from app.services.audit_service import AuditService
from app.services.state_diff import capture_state


class AlertService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        *,
        status: AlertStatus | None = None,
        severity: AuditEventSeverity | None = None,
        alert_type: AlertType | None = None,
        acta_id: str | None = None,
        polling_station_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[Alert]:
        stmt = select(Alert).order_by(Alert.created_at.desc())
        if status:
            stmt = stmt.where(Alert.status == status)
        if severity:
            stmt = stmt.where(Alert.severity == severity)
        if alert_type:
            stmt = stmt.where(Alert.alert_type == alert_type)
        if acta_id:
            stmt = stmt.where(Alert.acta_id == acta_id)
        if polling_station_id:
            stmt = stmt.where(Alert.polling_station_id == polling_station_id)
        if date_from:
            stmt = stmt.where(Alert.created_at >= date_from)
        if date_to:
            stmt = stmt.where(Alert.created_at <= date_to)
        return list(self.db.scalars(stmt))

    def get_required(self, alert_id: str) -> Alert:
        alert = self.db.get(Alert, alert_id)
        if not alert:
            raise NotFoundError("Alert not found", code="ALERT_NOT_FOUND")
        return alert

    def create_idempotent(
        self,
        *,
        alert_type: AlertType,
        severity: AuditEventSeverity,
        entity_type: str,
        entity_id: str,
        description: str,
        evidence: dict | None = None,
        recommendation: str | None = None,
        acta_id: str | None = None,
        polling_station_id: str | None = None,
        detected_by: str = "SYSTEM",
    ) -> Alert:
        existing = self.db.scalar(
            select(Alert).where(
                Alert.alert_type == alert_type,
                Alert.entity_type == entity_type,
                Alert.entity_id == entity_id,
                Alert.status.in_([AlertStatus.OPEN, AlertStatus.IN_REVIEW, AlertStatus.ESCALATED]),
            )
        )
        if existing:
            return existing
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            entity_type=entity_type,
            entity_id=entity_id,
            acta_id=acta_id,
            polling_station_id=polling_station_id,
            detected_by=detected_by,
            description=description,
            evidence=evidence,
            recommendation=recommendation,
        )
        self.db.add(alert)
        self.db.flush()
        return alert

    def assign(self, alert_id: str, assigned_to: str, actor_user_id: str, request_id: str) -> Alert:
        alert = self.get_required(alert_id)
        before = capture_state(alert)
        alert.assigned_to = assigned_to
        alert.status = AlertStatus.IN_REVIEW
        self.db.flush()
        AuditService(self.db).record(
            action="ALERT_ASSIGNED",
            entity_type="Alert",
            entity_id=alert.id,
            actor_user_id=actor_user_id,
            request_id=request_id,
            before_state=before,
            after_state=capture_state(alert),
            event_category=AuditEventCategory.SECURITY,
            event_severity=AuditEventSeverity.INFO,
            related_acta_id=alert.acta_id,
            related_polling_station_id=alert.polling_station_id,
        )
        return alert

    def resolve(self, alert_id: str, actor_user_id: str, request_id: str, notes: str, false_positive: bool = False) -> Alert:
        alert = self.get_required(alert_id)
        before = capture_state(alert)
        alert.status = AlertStatus.FALSE_POSITIVE if false_positive else AlertStatus.RESOLVED
        alert.resolved_by = actor_user_id
        alert.resolution_notes = notes
        alert.resolved_at = utc_now()
        self.db.flush()
        AuditService(self.db).record(
            action="ALERT_RESOLVED",
            entity_type="Alert",
            entity_id=alert.id,
            actor_user_id=actor_user_id,
            request_id=request_id,
            before_state=before,
            after_state=capture_state(alert),
            event_category=AuditEventCategory.SECURITY,
            event_severity=AuditEventSeverity.INFO,
            related_acta_id=alert.acta_id,
            related_polling_station_id=alert.polling_station_id,
        )
        return alert

    def escalate(self, alert_id: str, actor_user_id: str, request_id: str, notes: str | None = None) -> Alert:
        alert = self.get_required(alert_id)
        before = capture_state(alert)
        alert.status = AlertStatus.ESCALATED
        alert.evidence = {**(alert.evidence or {}), "escalation_notes": notes}
        self.db.flush()
        AuditService(self.db).record(
            action="ALERT_ESCALATED",
            entity_type="Alert",
            entity_id=alert.id,
            actor_user_id=actor_user_id,
            request_id=request_id,
            before_state=before,
            after_state=capture_state(alert),
            event_category=AuditEventCategory.SECURITY,
            event_severity=AuditEventSeverity.WARNING,
            related_acta_id=alert.acta_id,
            related_polling_station_id=alert.polling_station_id,
        )
        return alert
