from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests received by the API.",
    ["method", "route", "status_code", "role", "public_endpoint"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "route", "status_code", "role", "public_endpoint"],
)
HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed.",
    ["method", "route"],
)
HTTP_ERRORS_TOTAL = Counter(
    "http_errors_total",
    "Total HTTP responses with error status codes.",
    ["method", "route", "status_code"],
)
HTTP_RATE_LIMITED_TOTAL = Counter(
    "http_rate_limited_total",
    "Total requests rejected by rate limiting.",
    ["route", "endpoint_group"],
)

ACTAS_CREATED_TOTAL = Counter("actas_created_total", "Actas created.", ["municipality", "district", "election_type"])
ACTAS_PROCESSED_TOTAL = Counter("actas_processed_total", "Actas processed.", ["status", "municipality", "district", "election_type"])
ACTAS_VERIFIED_TOTAL = Counter("actas_verified_total", "Actas verified.", ["municipality", "district", "election_type"])
ACTAS_REJECTED_TOTAL = Counter("actas_rejected_total", "Actas rejected.", ["municipality", "district", "election_type"])
ACTAS_BY_STATUS = Gauge("actas_by_status", "Current acta count by status.", ["status", "municipality", "district", "election_type"])
ACTA_PROCESSING_DURATION_SECONDS = Histogram("acta_processing_duration_seconds", "Acta processing duration.", ["status"])

DOCUMENTS_UPLOADED_TOTAL = Counter("documents_uploaded_total", "Documents uploaded.", ["integrity_status", "storage_provider", "file_type"])
DOCUMENTS_VERIFIED_TOTAL = Counter("documents_verified_total", "Documents verified.", ["integrity_status", "storage_provider", "file_type"])
DOCUMENT_HASH_MISMATCHES_TOTAL = Counter("document_hash_mismatches_total", "Document hash mismatches detected.", ["storage_provider", "file_type"])
DOCUMENT_STORAGE_MISSING_TOTAL = Counter("document_storage_missing_total", "Missing document storage objects.", ["storage_provider"])
DOCUMENT_INTEGRITY_CHECKS_TOTAL = Counter("document_integrity_checks_total", "Document integrity checks.", ["integrity_status", "storage_provider"])
DOCUMENT_UPLOAD_SIZE_BYTES = Histogram("document_upload_size_bytes", "Uploaded document size in bytes.", ["storage_provider", "file_type"])

PREP_RESULTS_CAPTURED_TOTAL = Counter("prep_results_captured_total", "PREP results captured.", ["municipality", "district"])
PREP_RESULTS_VALIDATED_TOTAL = Counter("prep_results_validated_total", "PREP results validated.", ["validation_status", "municipality", "district"])
PREP_MISMATCHES_TOTAL = Counter("prep_mismatches_total", "PREP mismatches detected.", ["municipality", "district"])
PREP_REQUIRES_REVIEW_TOTAL = Counter("prep_requires_review_total", "PREP results requiring review.", ["municipality", "district"])

BLOCKCHAIN_ANCHOR_ATTEMPTS_TOTAL = Counter("blockchain_anchor_attempts_total", "Blockchain anchor attempts.", ["provider", "network", "anchor_type"])
BLOCKCHAIN_ANCHOR_SUCCESS_TOTAL = Counter("blockchain_anchor_success_total", "Successful blockchain anchors.", ["provider", "network", "anchor_type"])
BLOCKCHAIN_ANCHOR_FAILURES_TOTAL = Counter("blockchain_anchor_failures_total", "Failed blockchain anchors.", ["provider", "network", "anchor_type"])
BLOCKCHAIN_VERIFICATION_ATTEMPTS_TOTAL = Counter("blockchain_verification_attempts_total", "Blockchain verification attempts.", ["provider", "network", "verification_status"])
BLOCKCHAIN_VERIFICATION_FAILURES_TOTAL = Counter("blockchain_verification_failures_total", "Blockchain verification failures.", ["provider", "network"])
BLOCKCHAIN_ANCHOR_DURATION_SECONDS = Histogram("blockchain_anchor_duration_seconds", "Blockchain anchor duration.", ["provider", "network", "anchor_type"])

AUDIT_EVENTS_TOTAL = Counter("audit_events_total", "Audit events recorded.", ["event_category", "event_severity", "action"])
AUDIT_LOG_WRITE_FAILURES_TOTAL = Counter("audit_log_write_failures_total", "Audit log write failures.", ["action"])
AUDIT_TAMPER_ATTEMPTS_TOTAL = Counter("audit_tamper_attempts_total", "Audit tamper attempts detected.", ["action"])

AUTH_LOGIN_SUCCESS_TOTAL = Counter("auth_login_success_total", "Successful logins.", ["role", "endpoint_group"])
AUTH_LOGIN_FAILED_TOTAL = Counter("auth_login_failed_total", "Failed logins.", ["role", "endpoint_group", "reason"])
AUTH_FORBIDDEN_TOTAL = Counter("auth_forbidden_total", "Forbidden authorization attempts.", ["role", "endpoint_group", "reason"])
AUTH_UNAUTHORIZED_TOTAL = Counter("auth_unauthorized_total", "Unauthorized requests.", ["role", "endpoint_group", "reason"])
PUBLIC_RATE_LIMIT_EXCEEDED_TOTAL = Counter("public_rate_limit_exceeded_total", "Public rate limit exceeded.", ["endpoint_group", "reason"])
SUSPICIOUS_ACCESS_DETECTED_TOTAL = Counter("suspicious_access_detected_total", "Suspicious access events.", ["endpoint_group", "reason"])

ALERTS_CREATED_TOTAL = Counter("alerts_created_total", "Alerts created.", ["alert_type", "severity", "status"])
ALERTS_OPEN_TOTAL = Gauge("alerts_open_total", "Open alerts.", ["alert_type", "severity", "status"])
ALERTS_RESOLVED_TOTAL = Counter("alerts_resolved_total", "Alerts resolved.", ["alert_type", "severity", "status"])
ALERTS_ESCALATED_TOTAL = Counter("alerts_escalated_total", "Alerts escalated.", ["alert_type", "severity", "status"])


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST


def is_public_endpoint(path: str) -> str:
    public_prefixes = (
        "/api/v1/traceability/public",
        "/api/v1/blockchain/verify",
        "/api/v1/public",
        "/health",
        "/metrics",
    )
    return "true" if path.startswith(public_prefixes) else "false"


def endpoint_group(path: str) -> str:
    parts = [part for part in path.split("/") if part]
    if len(parts) >= 3 and parts[0] == "api" and parts[1] == "v1":
        return parts[2]
    return parts[0] if parts else "root"


def normalize_route(path: str) -> str:
    if path == "/metrics":
        return "/metrics"
    if path.startswith("/health"):
        return path
    return path

