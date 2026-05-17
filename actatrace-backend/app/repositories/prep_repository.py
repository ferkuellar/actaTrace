from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.prep_result import PREPResult
from app.repositories.base import BaseRepository


class PREPRepository(BaseRepository[PREPResult]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, PREPResult)

    def list_for_acta(self, acta_id: str) -> list[PREPResult]:
        return list(self.db.scalars(select(PREPResult).where(PREPResult.acta_id == acta_id)).all())
