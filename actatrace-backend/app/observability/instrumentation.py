from __future__ import annotations

from app.observability import metrics


AUDIT_ACTION_METRIC_MAP = {
    "DOCUMENT_HASH_MISMATCH": lambda: metrics.DOCUMENT_HASH_MISMATCHES_TOTAL.labels("unknown", "unknown").inc(),
    "PREP_ACTA_MISMATCH": lambda: metrics.PREP_MISMATCHES_TOTAL.labels("unknown", "unknown").inc(),
    "AUDIT_LOG_TAMPER_ATTEMPT": lambda: metrics.AUDIT_TAMPER_ATTEMPTS_TOTAL.labels("AUDIT_LOG_TAMPER_ATTEMPT").inc(),
    "BLOCKCHAIN_ANCHOR_FAILED": lambda: metrics.BLOCKCHAIN_ANCHOR_FAILURES_TOTAL.labels("unknown", "unknown", "unknown").inc(),
    "PUBLIC_RATE_LIMIT_EXCEEDED": lambda: metrics.PUBLIC_RATE_LIMIT_EXCEEDED_TOTAL.labels("public", "rate_limit").inc(),
}


def record_audit_metric(action: str, event_category: str, event_severity: str) -> None:
    metrics.AUDIT_EVENTS_TOTAL.labels(event_category, event_severity, action).inc()
    recorder = AUDIT_ACTION_METRIC_MAP.get(action)
    if recorder:
        recorder()
