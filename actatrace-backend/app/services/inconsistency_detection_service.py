from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.acta import Acta
from app.models.alert import Alert
from app.models.custody_event import CustodyEvent
from app.models.document import Document
from app.models.enums import (
    AlertType,
    AuditEventSeverity,
    CustodyEventType,
    DocumentIntegrityStatus,
    PREPValidationStatus,
)
from app.models.mixins import utc_now
from app.models.prep_result import PREPResult
from app.services.alert_service import AlertService


class InconsistencyDetectionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.alerts = AlertService(db)

    def detect_for_acta(self, acta_id: str) -> list[Alert]:
        if not settings.enable_alert_generation:
            return []
        alerts: list[Alert] = []
        acta = self.db.get(Acta, acta_id)
        if not acta:
            return alerts
        alerts.extend(self.detect_prep_mismatch(acta))
        alerts.extend(self.detect_duplicate_acta(acta))
        alerts.extend(self.detect_document_hash_issues(acta))
        alerts.extend(self.detect_custody_gaps(acta))
        return alerts

    def detect_prep_mismatch(self, acta: Acta) -> list[Alert]:
        created: list[Alert] = []
        for prep in acta.prep_results:
            expected = acta.expected_total_votes
            if expected is None or prep.validation_status == PREPValidationStatus.REQUIRES_REVIEW:
                alert = self.alerts.create_idempotent(
                    alert_type=AlertType.MANUAL_REVIEW_REQUIRED,
                    severity=AuditEventSeverity.WARNING,
                    entity_type="PREPResult",
                    entity_id=prep.id,
                    acta_id=acta.id,
                    polling_station_id=acta.polling_station_id,
                    description="PREP result requires manual review because acta structured totals are unavailable.",
                    evidence={"prep_total_votes": prep.total_votes, "acta_expected_total_votes": expected},
                    recommendation="Capture or validate structured acta totals before final verification.",
                )
                created.append(alert)
            elif prep.total_votes != expected:
                alert = self.alerts.create_idempotent(
                    alert_type=AlertType.PREP_ACTA_MISMATCH,
                    severity=AuditEventSeverity.CRITICAL,
                    entity_type="PREPResult",
                    entity_id=prep.id,
                    acta_id=acta.id,
                    polling_station_id=acta.polling_station_id,
                    description="PREP total votes do not match acta expected total votes.",
                    evidence={"prep_total_votes": prep.total_votes, "acta_expected_total_votes": expected},
                    recommendation="Supervisor must compare PREP capture with the source acta document.",
                )
                created.append(alert)
        return created

    def detect_duplicate_acta(self, acta: Acta) -> list[Alert]:
        count = self.db.scalar(select(func.count()).select_from(Acta).where(Acta.acta_code == acta.acta_code)) or 0
        if count <= 1:
            return []
        return [
            self.alerts.create_idempotent(
                alert_type=AlertType.DUPLICATE_ACTA,
                severity=AuditEventSeverity.CRITICAL,
                entity_type="Acta",
                entity_id=acta.id,
                acta_id=acta.id,
                polling_station_id=acta.polling_station_id,
                description="The same acta code appears more than once.",
                evidence={"acta_code": acta.acta_code, "count": count},
                recommendation="Block verification until supervisor resolves duplicate registration.",
            )
        ]

    def detect_document_hash_issues(self, acta: Acta) -> list[Alert]:
        if not acta.document:
            return []
        document = acta.document
        created: list[Alert] = []
        if document.integrity_status in {DocumentIntegrityStatus.MISMATCH, DocumentIntegrityStatus.CORRUPTED}:
            created.append(
                self.alerts.create_idempotent(
                    alert_type=AlertType.DOCUMENT_HASH_MISMATCH,
                    severity=AuditEventSeverity.CRITICAL,
                    entity_type="Document",
                    entity_id=document.id,
                    acta_id=acta.id,
                    polling_station_id=acta.polling_station_id,
                    description="Document integrity status indicates a hash mismatch or corruption.",
                    evidence={"sha256_hash": document.sha256_hash, "integrity_status": document.integrity_status.value},
                    recommendation="Re-hash the stored file and compare against database and blockchain proof.",
                )
            )
        if document.integrity_status == DocumentIntegrityStatus.STORAGE_MISSING:
            created.append(
                self.alerts.create_idempotent(
                    alert_type=AlertType.STORAGE_OBJECT_MISSING,
                    severity=AuditEventSeverity.CRITICAL,
                    entity_type="Document",
                    entity_id=document.id,
                    acta_id=acta.id,
                    polling_station_id=acta.polling_station_id,
                    description="Document metadata exists but storage object is missing.",
                    evidence={"sha256_hash": document.sha256_hash},
                    recommendation="Escalate to storage administrator and preserve audit trail.",
                )
            )
        duplicates = self.db.scalar(select(func.count()).select_from(Document).where(Document.sha256_hash == document.sha256_hash)) or 0
        if duplicates > 1:
            created.append(
                self.alerts.create_idempotent(
                    alert_type=AlertType.DUPLICATE_DOCUMENT_HASH,
                    severity=AuditEventSeverity.WARNING,
                    entity_type="Document",
                    entity_id=document.id,
                    acta_id=acta.id,
                    polling_station_id=acta.polling_station_id,
                    description="The same document hash appears in more than one document record.",
                    evidence={"sha256_hash": document.sha256_hash, "count": duplicates},
                    recommendation="Review whether this is a legitimate duplicate or duplicate registration attempt.",
                )
            )
        return created

    def detect_custody_gaps(self, acta: Acta) -> list[Alert]:
        created: list[Alert] = []
        threshold = timedelta(hours=settings.custody_reception_threshold_hours)
        events = sorted(acta.custody_events, key=lambda item: item.occurred_at)
        for event in events:
            if not event.performed_by:
                created.append(
                    self.alerts.create_idempotent(
                        alert_type=AlertType.CUSTODY_GAP,
                        severity=AuditEventSeverity.CRITICAL,
                        entity_type="CustodyEvent",
                        entity_id=event.id,
                        acta_id=acta.id,
                        polling_station_id=acta.polling_station_id,
                        description="Custody event has no responsible actor.",
                        evidence={"event_type": event.event_type.value},
                        recommendation="Reject or correct the custody event through supervisor workflow.",
                    )
                )
            if event.event_type != CustodyEventType.TRANSFERRED:
                continue
            reception = next(
                (
                    item
                    for item in events
                    if item.occurred_at > event.occurred_at
                    and item.event_type in {CustodyEventType.RECEIVED, CustodyEventType.VALIDATED, CustodyEventType.REJECTED}
                ),
                None,
            )
            now = utc_now()
            occurred_at = event.occurred_at
            if now.tzinfo is not None and occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=now.tzinfo)
            if reception is None and now - occurred_at > threshold:
                created.append(
                    self.alerts.create_idempotent(
                        alert_type=AlertType.CUSTODY_GAP,
                        severity=AuditEventSeverity.WARNING,
                        entity_type="CustodyEvent",
                        entity_id=event.id,
                        acta_id=acta.id,
                        polling_station_id=acta.polling_station_id,
                        description="Custody transfer has no reception event within the configured threshold.",
                        evidence={"occurred_at": event.occurred_at.isoformat(), "threshold_hours": threshold.total_seconds() / 3600},
                        recommendation="Contact receiving actor and record reception, rejection, or escalation.",
                    )
                )
        return created
