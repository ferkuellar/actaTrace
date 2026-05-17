from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.custody_event import CustodyEvent
from app.repositories.base import BaseRepository


class CustodyRepository(BaseRepository[CustodyEvent]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, CustodyEvent)

    def timeline_for_acta(self, acta_id: str) -> list[CustodyEvent]:
        return list(
            self.db.scalars(
                select(CustodyEvent)
                .where(CustodyEvent.acta_id == acta_id)
                .order_by(CustodyEvent.occurred_at.asc())
            ).all()
        )
