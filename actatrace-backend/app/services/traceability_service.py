from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import NotFoundError
from app.models.acta import Acta
from app.models.alert import Alert
from app.models.audit_log import AuditLog
from app.models.blockchain_anchor import BlockchainAnchor
from app.models.custody_event import CustodyEvent
from app.models.document import Document
from app.models.polling_station import PollingStation
from app.models.prep_result import PREPResult
from app.services.inconsistency_detection_service import InconsistencyDetectionService


class TraceabilityService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def acta_timeline(self, acta_id: str) -> list[dict[str, Any]]:
        acta = self.db.get(Acta, acta_id)
        if not acta:
            raise NotFoundError("Acta not found", code="ACTA_NOT_FOUND")
        InconsistencyDetectionService(self.db).detect_for_acta(acta_id)
        events: list[dict[str, Any]] = []
        events.extend(self._audit_events(acta))
        events.extend(self._custody_events(acta))
        events.extend(self._prep_events(acta))
        events.extend(self._blockchain_events(acta))
        events.extend(self._alert_events(acta))
        return sorted(events, key=lambda item: item["timestamp"])

    def public_timeline_by_acta_code(self, acta_code: str) -> list[dict[str, Any]]:
        if not settings.enable_public_traceability:
            return []
        acta = self.db.scalar(select(Acta).where(Acta.acta_code == acta_code))
        if not acta:
            raise NotFoundError("Acta not found", code="ACTA_NOT_FOUND")
        return [self._redact_public(event, acta) for event in self.acta_timeline(acta.id)]

    def polling_station_traceability(self, polling_station_id: str) -> dict[str, Any]:
        station = self.db.get(PollingStation, polling_station_id)
        if not station:
            raise NotFoundError("Polling station not found", code="POLLING_STATION_NOT_FOUND")
        return {
            "polling_station": {
                "id": station.id,
                "polling_station_code": station.polling_station_code,
                "state": station.state,
                "municipality": station.municipality,
                "district": station.district,
                "section": station.section,
            },
            "actas": [{"id": acta.id, "acta_code": acta.acta_code, "status": acta.status.value} for acta in station.actas],
            "prep_results": [
                {"id": prep.id, "acta_id": prep.acta_id, "validation_status": prep.validation_status.value, "total_votes": prep.total_votes}
                for prep in station.prep_results
            ],
        }

    def audit_search(
        self,
        *,
        entity_type: str | None = None,
        entity_id: str | None = None,
        actor_user_id: str | None = None,
        event_category: str | None = None,
        event_severity: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        request_id: str | None = None,
        correlation_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        if entity_type:
            stmt = stmt.where(AuditLog.entity_type == entity_type)
        if entity_id:
            stmt = stmt.where(AuditLog.entity_id == entity_id)
        if actor_user_id:
            stmt = stmt.where(AuditLog.actor_user_id == actor_user_id)
        if event_category:
            stmt = stmt.where(AuditLog.event_category == event_category)
        if event_severity:
            stmt = stmt.where(AuditLog.event_severity == event_severity)
        if date_from:
            stmt = stmt.where(AuditLog.created_at >= date_from)
        if date_to:
            stmt = stmt.where(AuditLog.created_at <= date_to)
        if request_id:
            stmt = stmt.where(AuditLog.request_id == request_id)
        if correlation_id:
            stmt = stmt.where(AuditLog.correlation_id == correlation_id)
        return list(self.db.scalars(stmt))

    def _audit_events(self, acta: Acta) -> list[dict[str, Any]]:
        ids = [acta.id]
        if acta.document_id:
            ids.append(acta.document_id)
        rows = self.db.scalars(
            select(AuditLog).where(
                (AuditLog.related_acta_id == acta.id)
                | ((AuditLog.entity_type == "Acta") & (AuditLog.entity_id == acta.id))
                | ((AuditLog.entity_type == "Document") & (AuditLog.entity_id.in_(ids)))
            )
        )
        return [
            {
                "id": log.id,
                "event_type": log.action,
                "event_category": log.event_category.value,
                "severity": log.event_severity.value,
                "timestamp": log.created_at,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "actor": {"user_id": log.actor_user_id, "role": log.actor_role, "organization": log.actor_organization},
                "location": log.geo_location,
                "before_state": log.before_state,
                "after_state": log.after_state,
                "evidence": {"hash_value": log.hash_value, "document_id": log.evidence_document_id, "blockchain_anchor_id": log.blockchain_anchor_id},
                "verification_status": (log.metadata_json or {}).get("verification_status"),
            }
            for log in rows
        ]

    def _custody_events(self, acta: Acta) -> list[dict[str, Any]]:
        return [
            {
                "id": event.id,
                "event_type": f"CUSTODY_{event.event_type.value}",
                "event_category": "CUSTODY",
                "severity": "INFO",
                "timestamp": event.occurred_at,
                "entity_type": "CustodyEvent",
                "entity_id": event.id,
                "actor": {"user_id": event.performed_by},
                "location": event.location,
                "before_state": None,
                "after_state": {"event_type": event.event_type.value},
                "evidence": {"document_id": event.evidence_document_id},
                "verification_status": "RECORDED",
            }
            for event in acta.custody_events
        ]

    def _prep_events(self, acta: Acta) -> list[dict[str, Any]]:
        return [
            {
                "id": prep.id,
                "event_type": "PREP_RESULT_CAPTURED",
                "event_category": "PREP",
                "severity": "WARNING" if prep.validation_status.value in {"MISMATCHED", "REQUIRES_REVIEW"} else "INFO",
                "timestamp": prep.captured_at,
                "entity_type": "PREPResult",
                "entity_id": prep.id,
                "actor": {"user_id": prep.captured_by},
                "location": None,
                "before_state": None,
                "after_state": {"total_votes": prep.total_votes, "validation_status": prep.validation_status.value},
                "evidence": {"mismatch_reason": prep.mismatch_reason},
                "verification_status": prep.validation_status.value,
            }
            for prep in acta.prep_results
        ]

    def _blockchain_events(self, acta: Acta) -> list[dict[str, Any]]:
        anchors = list(self.db.scalars(select(BlockchainAnchor).where((BlockchainAnchor.entity_id == acta.id) | (BlockchainAnchor.entity_id == acta.document_id))))
        return [
            {
                "id": anchor.id,
                "event_type": "BLOCKCHAIN_ANCHOR_RECORDED",
                "event_category": "BLOCKCHAIN",
                "severity": "INFO" if anchor.verification_status.value in {"ANCHORED", "VERIFIED"} else "WARNING",
                "timestamp": anchor.anchored_at or anchor.created_at,
                "entity_type": "BlockchainAnchor",
                "entity_id": anchor.id,
                "actor": {"user_id": anchor.anchored_by},
                "location": anchor.blockchain_network,
                "before_state": None,
                "after_state": {"transaction_hash": anchor.transaction_hash, "verification_status": anchor.verification_status.value},
                "evidence": {"hash_value": anchor.hash_value, "provider": anchor.provider.value},
                "verification_status": anchor.verification_status.value,
            }
            for anchor in anchors
        ]

    def _alert_events(self, acta: Acta) -> list[dict[str, Any]]:
        alerts = self.db.scalars(select(Alert).where(Alert.acta_id == acta.id))
        return [
            {
                "id": alert.id,
                "event_type": alert.alert_type.value,
                "event_category": "SECURITY",
                "severity": alert.severity.value,
                "timestamp": alert.created_at,
                "entity_type": "Alert",
                "entity_id": alert.id,
                "actor": {"detected_by": alert.detected_by},
                "location": None,
                "before_state": None,
                "after_state": {"status": alert.status.value},
                "evidence": alert.evidence,
                "verification_status": alert.status.value,
            }
            for alert in alerts
        ]

    def _redact_public(self, event: dict[str, Any], acta: Acta) -> dict[str, Any]:
        return {
            "acta_code": acta.acta_code,
            "polling_station_code": acta.polling_station.polling_station_code if acta.polling_station else None,
            "event_type": event["event_type"],
            "timestamp": event["timestamp"],
            "verification_status": event.get("verification_status"),
            "severity": event["severity"] if event["severity"] != "CRITICAL" else "REVIEW_REQUIRED",
            "hash_proof": {"hash_value": (event.get("evidence") or {}).get("hash_value")},
            "public_document_status": acta.document.access_status.value if acta.document else None,
            "blockchain_anchor_proof": {"anchor_id": (event.get("evidence") or {}).get("blockchain_anchor_id")},
        }


class ForensicReportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.traceability = TraceabilityService(db)

    def acta_report(self, acta_id: str) -> dict[str, Any]:
        acta = self.db.get(Acta, acta_id)
        if not acta:
            raise NotFoundError("Acta not found", code="ACTA_NOT_FOUND")
        alerts = InconsistencyDetectionService(self.db).detect_for_acta(acta_id)
        timeline = self.traceability.acta_timeline(acta_id)
        document = acta.document
        anchors = list(self.db.scalars(select(BlockchainAnchor).where((BlockchainAnchor.entity_id == acta.id) | (BlockchainAnchor.entity_id == acta.document_id))))
        return {
            "acta": {
                "id": acta.id,
                "acta_code": acta.acta_code,
                "status": acta.status.value,
                "polling_station_id": acta.polling_station_id,
                "expected_total_votes": acta.expected_total_votes,
            },
            "document": None
            if not document
            else {
                "id": document.id,
                "file_name": document.file_name,
                "mime_type": document.mime_type,
                "sha256_hash": document.sha256_hash,
                "integrity_status": document.integrity_status.value,
                "access_status": document.access_status.value,
            },
            "custody_timeline": [event for event in timeline if event["event_category"] == "CUSTODY"],
            "prep_results": [
                {"id": prep.id, "total_votes": prep.total_votes, "validation_status": prep.validation_status.value, "mismatch_reason": prep.mismatch_reason}
                for prep in acta.prep_results
            ],
            "hash_verification_status": {
                "database_hash": document.sha256_hash if document else None,
                "integrity_status": document.integrity_status.value if document else "MISSING",
            },
            "blockchain_anchor_status": {
                "anchors": [
                    {
                        "id": anchor.id,
                        "hash_value": anchor.hash_value,
                        "transaction_hash": anchor.transaction_hash,
                        "verification_status": anchor.verification_status.value,
                    }
                    for anchor in anchors
                ]
            },
            "inconsistencies": [{"alert_type": alert.alert_type.value, "severity": alert.severity.value, "description": alert.description} for alert in alerts],
            "alerts": [{"id": alert.id, "alert_type": alert.alert_type.value, "status": alert.status.value} for alert in alerts],
            "audit_summary": {
                "event_count": len(timeline),
                "critical_events": len([event for event in timeline if event["severity"] in {"CRITICAL", "REVIEW_REQUIRED"}]),
            },
            "generated_at": datetime.now(timezone.utc),
        }
