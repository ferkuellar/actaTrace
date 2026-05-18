from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.audit_log import AuditLog


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def basic_health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "timestamp": utc_now_iso(),
    }


def check_database(db: Session) -> dict[str, Any]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


def check_audit_log_readiness(db: Session) -> dict[str, Any]:
    db.query(AuditLog.id).limit(1).all()
    return {"status": "ok"}


def readiness_report(db: Session) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    overall = "ready"
    for name, check in {
        "database": lambda: check_database(db),
        "audit_log": lambda: check_audit_log_readiness(db),
        "storage_provider": lambda: {"status": "configured", "provider": settings.storage_provider},
        "blockchain_provider": lambda: {"status": "configured", "provider": settings.blockchain_provider},
    }.items():
        try:
            checks[name] = check()
        except Exception as exc:
            checks[name] = {"status": "failed", "error": exc.__class__.__name__}
            overall = "not_ready"
    return {
        "status": overall,
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "timestamp": utc_now_iso(),
        "checks": checks,
    }

