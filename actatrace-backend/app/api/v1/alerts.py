from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_request_id, require_roles
from app.core.database import get_db
from app.models.enums import AlertStatus, AlertType, AuditEventSeverity, UserRole
from app.models.user import User
from app.schemas.alert import AlertAssignRequest, AlertEscalateRequest, AlertRead, AlertResolveRequest
from app.services.alert_service import AlertService

router = APIRouter()


@router.get("", response_model=list[AlertRead])
def list_alerts(
    status: AlertStatus | None = None,
    severity: AuditEventSeverity | None = None,
    alert_type: AlertType | None = None,
    acta_id: str | None = None,
    polling_station_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    return AlertService(db).list(
        status=status,
        severity=severity,
        alert_type=alert_type,
        acta_id=acta_id,
        polling_station_id=polling_station_id,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    return AlertService(db).get_required(alert_id)


@router.patch("/{alert_id}/assign", response_model=AlertRead)
def assign_alert(
    alert_id: str,
    payload: AlertAssignRequest,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    alert = AlertService(db).assign(alert_id, payload.assigned_to, current_user.id, request_id)
    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/{alert_id}/resolve", response_model=AlertRead)
def resolve_alert(
    alert_id: str,
    payload: AlertResolveRequest,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    alert = AlertService(db).resolve(alert_id, current_user.id, request_id, payload.resolution_notes, payload.false_positive)
    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/{alert_id}/escalate", response_model=AlertRead)
def escalate_alert(
    alert_id: str,
    payload: AlertEscalateRequest,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(require_roles(UserRole.SUPERVISOR, UserRole.AUDITOR)),
):
    alert = AlertService(db).escalate(alert_id, current_user.id, request_id, payload.notes)
    db.commit()
    db.refresh(alert)
    return alert
