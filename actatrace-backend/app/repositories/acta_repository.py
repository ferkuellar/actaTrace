from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.acta import Acta
from app.repositories.base import BaseRepository


class ActaRepository(BaseRepository[Acta]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Acta)

    def get_by_code(self, acta_code: str) -> Acta | None:
        return self.db.scalar(select(Acta).where(Acta.acta_code == acta_code))
