import json
import logging

from app.models.enums import AuditEventCategory, AuditEventSeverity, UserRole
from app.observability.logging_config import JsonFormatter
from app.observability.metrics import DOCUMENT_HASH_MISMATCHES_TOTAL, render_metrics
from app.services.audit_service import AuditService
from app.tests.conftest import create_user


def test_health_ready_checks_database(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["checks"]["database"]["status"] == "ok"


def test_metrics_exposes_prometheus_format(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "http_requests_total" in response.text


def test_api_request_increments_http_requests_total(client):
    client.get("/health")
    body, _ = render_metrics()
    assert b'http_requests_total{method="GET",public_endpoint="true"' in body


def test_error_response_increments_http_errors_total(client):
    client.get("/does-not-exist")
    body, _ = render_metrics()
    assert b"http_errors_total" in body
    assert b'status_code="404"' in body


def test_hash_mismatch_audit_event_increments_metric(db):
    before = DOCUMENT_HASH_MISMATCHES_TOTAL.labels("unknown", "unknown")._value.get()
    AuditService(db).record(
        action="DOCUMENT_HASH_MISMATCH",
        entity_type="Document",
        entity_id="doc-1",
        actor_user_id=None,
        request_id="req-1",
        event_category=AuditEventCategory.DOCUMENT,
        event_severity=AuditEventSeverity.CRITICAL,
    )
    after = DOCUMENT_HASH_MISMATCHES_TOTAL.labels("unknown", "unknown")._value.get()
    assert after == before + 1


def test_failed_login_increments_auth_metric(client, db):
    create_user(db, UserRole.ADMIN_ELECTORAL)
    client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "wrong-password"})
    body, _ = render_metrics()
    assert b"auth_login_failed_total" in body
    assert b'reason="invalid_credentials"' in body


def test_structured_logs_include_request_id_and_mask_secrets():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="actatrace.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="security_event",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-123"
    record.password = "plaintext"
    record.token = "secret-token"
    payload = json.loads(formatter.format(record))
    assert payload["request_id"] == "req-123"
    assert payload["password"] == "***"
    assert payload["token"] == "***"
