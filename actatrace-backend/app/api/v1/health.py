from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.observability.health import basic_health, readiness_report

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return basic_health()


@router.get("/health/live")
def live() -> dict:
    return {"status": "alive"}


@router.get("/health/ready")
def ready(response: Response, db: Session = Depends(get_db)) -> dict:
    report = readiness_report(db)
    if report["status"] != "ready":
        response.status_code = 503
    return report

