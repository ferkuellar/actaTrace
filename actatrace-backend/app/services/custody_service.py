from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.custody_event import CustodyEvent
from app.repositories.acta_repository import ActaRepository
from app.repositories.custody_repository import CustodyRepository
from app.schemas.custody_event import CustodyEventCreate
from app.services.audit_service import AuditService


class CustodyService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = CustodyRepository(db)
        self.actas = ActaRepository(db)
        self.audit = AuditService(db)

    def create(self, payload: CustodyEventCreate, user_id: str, request_id: str) -> CustodyEvent:
        if not self.actas.get(payload.acta_id):
            raise NotFoundError("Acta not found", code="ACTA_NOT_FOUND")
        event = CustodyEvent(**payload.model_dump(), performed_by=user_id)
        self.events.add(event)
        self.audit.record(
            action="CUSTODY_EVENT_CREATED",
            entity_type="CUSTODY_EVENT",
            entity_id=event.id,
            actor_user_id=user_id,
            request_id=request_id,
            after_state={"acta_id": event.acta_id, "event_type": event.event_type.value},
        )
        return event
