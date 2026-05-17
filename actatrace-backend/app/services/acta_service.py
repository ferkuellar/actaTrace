from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.acta import Acta
from app.models.enums import ActaStatus, DocumentIntegrityStatus
from app.repositories.acta_repository import ActaRepository
from app.schemas.acta import ActaCreate, ActaUpdate
from app.services.audit_service import AuditService


class ActaService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.actas = ActaRepository(db)
        self.audit = AuditService(db)

    def create(self, payload: ActaCreate, user_id: str, request_id: str) -> Acta:
        if self.actas.get_by_code(payload.acta_code):
            raise ConflictError("Acta code already exists", code="ACTA_CODE_EXISTS")
        status = ActaStatus.UPLOADED if payload.document_id else ActaStatus.DRAFT
        acta = Acta(**payload.model_dump(), created_by=user_id, status=status)
        self.actas.add(acta)
        self.audit.record(
            action="ACTA_CREATED",
            entity_type="ACTA",
            entity_id=acta.id,
            actor_user_id=user_id,
            request_id=request_id,
            after_state={"acta_code": acta.acta_code, "status": acta.status.value},
        )
        return acta

    def update(self, acta_id: str, payload: ActaUpdate, user_id: str, request_id: str) -> Acta:
        acta = self.actas.get(acta_id)
        if not acta:
            raise NotFoundError("Acta not found", code="ACTA_NOT_FOUND")
        if acta.status == ActaStatus.VERIFIED:
            raise ConflictError("Verified actas cannot be edited directly", code="ACTA_VERIFIED_IMMUTABLE")
        before = {"document_id": acta.document_id, "expected_total_votes": acta.expected_total_votes, "status": acta.status.value}
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(acta, key, value)
        if acta.document_id and acta.status == ActaStatus.DRAFT:
            acta.status = ActaStatus.UPLOADED
        self.audit.record(
            action="ACTA_UPDATED",
            entity_type="ACTA",
            entity_id=acta.id,
            actor_user_id=user_id,
            request_id=request_id,
            before_state=before,
            after_state={"document_id": acta.document_id, "expected_total_votes": acta.expected_total_votes, "status": acta.status.value},
        )
        self.db.flush()
        return acta

    def verify_hash(self, acta_id: str, user_id: str, request_id: str) -> Acta:
        acta = self.actas.get(acta_id)
        if not acta:
            raise NotFoundError("Acta not found", code="ACTA_NOT_FOUND")
        if not acta.document:
            raise ConflictError("Acta has no document", code="ACTA_DOCUMENT_REQUIRED")
        if acta.document.integrity_status not in {DocumentIntegrityStatus.VALID, DocumentIntegrityStatus.PENDING}:
            self.audit.record(
                action="ACTA_DOCUMENT_HASH_MISMATCH",
                entity_type="ACTA",
                entity_id=acta.id,
                actor_user_id=user_id,
                request_id=request_id,
                after_state={"document_integrity_status": acta.document.integrity_status.value},
            )
            raise ConflictError("Document integrity is not valid", code="DOCUMENT_INTEGRITY_INVALID")
        before = {"status": acta.status.value}
        acta.status = ActaStatus.HASHED
        self.audit.record(
            action="ACTA_HASH_VERIFIED",
            entity_type="ACTA",
            entity_id=acta.id,
            actor_user_id=user_id,
            request_id=request_id,
            before_state=before,
            after_state={"status": acta.status.value, "sha256_hash": acta.document.sha256_hash},
        )
        self.db.flush()
        return acta

    def submit_review(self, acta_id: str, user_id: str, request_id: str) -> Acta:
        return self._transition(acta_id, ActaStatus.UNDER_REVIEW, "ACTA_SUBMITTED_FOR_REVIEW", user_id, request_id)

    def approve(self, acta_id: str, user_id: str, request_id: str) -> Acta:
        acta = self._transition(acta_id, ActaStatus.VERIFIED, "ACTA_APPROVED", user_id, request_id)
        acta.verified_at = datetime.now(timezone.utc)
        self.db.flush()
        return acta

    def reject(self, acta_id: str, reason: str, user_id: str, request_id: str) -> Acta:
        return self._transition(acta_id, ActaStatus.REJECTED, "ACTA_REJECTED", user_id, request_id, {"reason": reason})

    def _transition(self, acta_id: str, status: ActaStatus, action: str, user_id: str, request_id: str, extra: dict | None = None) -> Acta:
        acta = self.actas.get(acta_id)
        if not acta:
            raise NotFoundError("Acta not found", code="ACTA_NOT_FOUND")
        before = {"status": acta.status.value}
        acta.status = status
        after = {"status": acta.status.value}
        if extra:
            after.update(extra)
        self.audit.record(
            action=action,
            entity_type="ACTA",
            entity_id=acta.id,
            actor_user_id=user_id,
            request_id=request_id,
            before_state=before,
            after_state=after,
        )
        self.db.flush()
        return acta
