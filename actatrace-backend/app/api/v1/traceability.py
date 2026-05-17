from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.audit import AuditLogRead, ForensicReportRead, TraceabilityEventRead
from app.services.traceability_service import ForensicReportService, TraceabilityService

router = APIRouter()


@router.get("/actas/{acta_id}/timeline", response_model=list[TraceabilityEventRead])
def acta_timeline(
    acta_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    return TraceabilityService(db).acta_timeline(acta_id)


@router.get("/actas/{acta_id}/forensic-report", response_model=ForensicReportRead)
def acta_forensic_report(
    acta_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    return ForensicReportService(db).acta_report(acta_id)


@router.get("/polling-stations/{polling_station_id}")
def polling_station_traceability(
    polling_station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR, UserRole.OBSERVADOR)),
):
    return TraceabilityService(db).polling_station_traceability(polling_station_id)


@router.get("/audit-events", response_model=list[AuditLogRead])
def audit_events(
    entity_type: str | None = None,
    entity_id: str | None = None,
    actor_user_id: str | None = None,
    event_category: str | None = None,
    event_severity: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    request_id: str | None = None,
    correlation_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    return TraceabilityService(db).audit_search(
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        event_category=event_category,
        event_severity=event_severity,
        date_from=date_from,
        date_to=date_to,
        request_id=request_id,
        correlation_id=correlation_id,
        limit=limit,
        offset=offset,
    )


@router.get("/public/actas/{acta_code}")
def public_acta_timeline(
    acta_code: str,
    db: Session = Depends(get_db),
):
    return TraceabilityService(db).public_timeline_by_acta_code(acta_code)
