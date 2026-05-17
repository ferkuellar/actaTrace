from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Document)

    def get_by_hash(self, sha256_hash: str) -> Document | None:
        return self.db.scalar(select(Document).where(Document.sha256_hash == sha256_hash))
