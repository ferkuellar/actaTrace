from datetime import timedelta

import pytest

from app.models.acta import Acta
from app.models.alert import Alert
from app.models.audit_log import AuditLog
from app.models.custody_event import CustodyEvent
from app.models.document import Document
from app.models.enums import (
    ActaStatus,
    AlertStatus,
    AlertType,
    AuditEventCategory,
    AuditEventSeverity,
    CustodyEventType,
    DocumentAccessStatus,
    DocumentIntegrityStatus,
    DocumentLifecycleStatus,
    PREPValidationStatus,
    UserRole,
)
from app.models.mixins import utc_now
from app.models.prep_result import PREPResult
from app.services.alert_service import AlertService
from app.services.inconsistency_detection_service import InconsistencyDetectionService
from app.services.traceability_service import ForensicReportService
from app.tests.conftest import auth_headers, create_polling_station, create_user


def _create_acta(db, user, station, *, expected_total_votes=100):
    acta = Acta(
        acta_code=f"ACTA-{station.section}-{expected_total_votes}",
        polling_station_id=station.id,
        status=ActaStatus.UPLOADED,
        election_type="MUNICIPAL",
        municipality=station.municipality,
        district=station.district,
        section=station.section,
        expected_total_votes=expected_total_votes,
        created_by=user.id,
    )
    db.add(acta)
    db.commit()
    db.refresh(acta)
    return acta


def _create_document(db, user, acta, *, integrity_status=DocumentIntegrityStatus.VALID):
    document = Document(
        file_name="acta.pdf",
        original_file_name="acta-original.pdf",
        file_type="application/pdf",
        mime_type="application/pdf",
        file_size=128,
        storage_provider="local",
        storage_path=f"local://{acta.id}/doc.pdf",
        storage_key=f"actas/{acta.id}/doc.pdf",
        sha256_hash="a" * 64,
        uploaded_by=user.id,
        integrity_status=integrity_status,
        access_status=DocumentAccessStatus.PUBLIC_VERIFIABLE,
        lifecycle_status=DocumentLifecycleStatus.VERIFIED,
    )
    db.add(document)
    db.flush()
    acta.document_id = document.id
    db.commit()
    db.refresh(acta)
    return document


def test_audit_log_is_append_only(db):
    user = create_user(db, UserRole.AUDITOR)
    log = AuditLog(
        actor_user_id=user.id,
        action="ACTA_CREATED",
        entity_type="Acta",
        entity_id="entity-1",
        request_id="req-1",
        event_category=AuditEventCategory.ACTA,
        event_severity=AuditEventSeverity.INFO,
    )
    db.add(log)
    db.commit()

    log.action = "TAMPERED"
    with pytest.raises(ValueError):
        db.commit()
    db.rollback()

    db.delete(log)
    with pytest.raises(ValueError):
        db.commit()


def test_acta_timeline_returns_chronological_events(client, db):
    user = create_user(db, UserRole.AUDITOR)
    station = create_polling_station(db)
    acta = _create_acta(db, user, station)
    older = utc_now() - timedelta(hours=2)
    newer = utc_now() - timedelta(hours=1)
    db.add_all(
        [
            CustodyEvent(acta_id=acta.id, event_type=CustodyEventType.CREATED, performed_by=user.id, occurred_at=newer),
            CustodyEvent(acta_id=acta.id, event_type=CustodyEventType.TRANSFERRED, performed_by=user.id, occurred_at=older),
        ]
    )
    db.commit()

    response = client.get(f"/api/v1/traceability/actas/{acta.id}/timeline", headers=auth_headers(client))
    assert response.status_code == 200, response.text
    timestamps = [item["timestamp"] for item in response.json()]
    assert timestamps == sorted(timestamps)


def test_forensic_report_includes_core_sections(client, db):
    user = create_user(db, UserRole.AUDITOR)
    station = create_polling_station(db)
    acta = _create_acta(db, user, station)
    _create_document(db, user, acta)

    response = client.get(f"/api/v1/traceability/actas/{acta.id}/forensic-report", headers=auth_headers(client))
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["acta"]["id"] == acta.id
    assert payload["document"]["sha256_hash"] == "a" * 64
    assert "custody_timeline" in payload
    assert "blockchain_anchor_status" in payload


def test_prep_mismatch_creates_alert(db):
    user = create_user(db, UserRole.AUDITOR)
    station = create_polling_station(db)
    acta = _create_acta(db, user, station, expected_total_votes=100)
    prep = PREPResult(
        acta_id=acta.id,
        polling_station_id=station.id,
        captured_by=user.id,
        candidate_results={"A": 40, "B": 30},
        total_votes=80,
        null_votes=10,
        valid_votes=70,
        captured_at=utc_now(),
        validation_status=PREPValidationStatus.MISMATCHED,
    )
    db.add(prep)
    db.commit()

    alerts = InconsistencyDetectionService(db).detect_for_acta(acta.id)
    assert any(alert.alert_type == AlertType.PREP_ACTA_MISMATCH for alert in alerts)


def test_document_hash_mismatch_creates_critical_alert(db):
    user = create_user(db, UserRole.AUDITOR)
    station = create_polling_station(db)
    acta = _create_acta(db, user, station)
    document = _create_document(db, user, acta, integrity_status=DocumentIntegrityStatus.MISMATCH)

    alerts = InconsistencyDetectionService(db).detect_for_acta(acta.id)
    alert = next(item for item in alerts if item.entity_id == document.id)
    assert alert.alert_type == AlertType.DOCUMENT_HASH_MISMATCH
    assert alert.severity == AuditEventSeverity.CRITICAL


def test_custody_gap_creates_warning_alert(db):
    user = create_user(db, UserRole.AUDITOR)
    station = create_polling_station(db)
    acta = _create_acta(db, user, station)
    db.add(
        CustodyEvent(
            acta_id=acta.id,
            event_type=CustodyEventType.TRANSFERRED,
            performed_by=user.id,
            occurred_at=utc_now() - timedelta(hours=12),
        )
    )
    db.commit()

    alerts = InconsistencyDetectionService(db).detect_for_acta(acta.id)
    assert any(alert.alert_type == AlertType.CUSTODY_GAP and alert.severity == AuditEventSeverity.WARNING for alert in alerts)


def test_public_timeline_redacts_sensitive_fields(client, db):
    user = create_user(db, UserRole.AUDITOR)
    station = create_polling_station(db)
    acta = _create_acta(db, user, station)
    _create_document(db, user, acta)
    db.add(
        AuditLog(
            actor_user_id=user.id,
            actor_role=user.role.value,
            action="DOCUMENT_RETRIEVED",
            entity_type="Document",
            entity_id=acta.document_id,
            related_acta_id=acta.id,
            request_id="req-redact",
            ip_address="127.0.0.1",
            user_agent="pytest",
            hash_value="a" * 64,
        )
    )
    db.commit()

    response = client.get(f"/api/v1/traceability/public/actas/{acta.acta_code}")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload
    assert "actor" not in payload[0]
    assert "ip_address" not in payload[0]
    assert "hash_proof" in payload[0]


def test_alert_assignment_creates_audit_event(client, db):
    user = create_user(db, UserRole.AUDITOR)
    alert = Alert(
        alert_type=AlertType.MANUAL_REVIEW_REQUIRED,
        severity=AuditEventSeverity.WARNING,
        status=AlertStatus.OPEN,
        entity_type="Acta",
        entity_id="acta-1",
        detected_by="pytest",
        description="Manual review required",
    )
    db.add(alert)
    db.commit()

    response = client.patch(f"/api/v1/alerts/{alert.id}/assign", json={"assigned_to": user.id}, headers=auth_headers(client))
    assert response.status_code == 200, response.text
    assert db.query(AuditLog).filter(AuditLog.action == "ALERT_ASSIGNED").count() == 1


def test_alert_resolution_requires_notes(client, db):
    create_user(db, UserRole.AUDITOR)
    alert = AlertService(db).create_idempotent(
        alert_type=AlertType.MANUAL_REVIEW_REQUIRED,
        severity=AuditEventSeverity.WARNING,
        entity_type="Acta",
        entity_id="acta-1",
        description="Manual review required",
    )
    db.commit()

    response = client.patch(f"/api/v1/alerts/{alert.id}/resolve", json={"resolution_notes": "bad"}, headers=auth_headers(client))
    assert response.status_code == 422
