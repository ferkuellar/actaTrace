from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.enums import PREPValidationStatus
from app.models.prep_result import PREPResult
from app.repositories.acta_repository import ActaRepository
from app.repositories.prep_repository import PREPRepository
from app.schemas.prep_result import PREPResultCreate
from app.services.audit_service import AuditService


class PREPService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.prep = PREPRepository(db)
        self.actas = ActaRepository(db)
        self.audit = AuditService(db)

    def create(self, payload: PREPResultCreate, user_id: str, request_id: str) -> PREPResult:
        acta = self.actas.get(payload.acta_id)
        if not acta:
            raise NotFoundError("Acta not found", code="ACTA_NOT_FOUND")
        if acta.polling_station_id != payload.polling_station_id:
            raise ConflictError("PREP polling station must match acta polling station", code="PREP_POLLING_STATION_MISMATCH")
        result = PREPResult(**payload.model_dump(), captured_by=user_id)
        self.prep.add(result)
        self.audit.record(
            action="PREP_RESULT_CREATED",
            entity_type="PREP_RESULT",
            entity_id=result.id,
            actor_user_id=user_id,
            request_id=request_id,
            after_state={"acta_id": result.acta_id, "total_votes": result.total_votes},
        )
        return result

    def validate(self, prep_result_id: str, user_id: str, request_id: str) -> PREPResult:
        result = self.prep.get(prep_result_id)
        if not result:
            raise NotFoundError("PREP result not found", code="PREP_RESULT_NOT_FOUND")
        before = {"validation_status": result.validation_status.value}
        acta = self.actas.get(result.acta_id)
        mismatch_reason = None
        if acta and acta.expected_total_votes is not None and acta.expected_total_votes != result.total_votes:
            result.validation_status = PREPValidationStatus.MISMATCHED
            mismatch_reason = "PREP total_votes does not match acta expected_total_votes"
        else:
            result.validation_status = PREPValidationStatus.MATCHED
        result.mismatch_reason = mismatch_reason
        self.audit.record(
            action="PREP_RESULT_VALIDATED" if not mismatch_reason else "PREP_RESULT_MISMATCH",
            entity_type="PREP_RESULT",
            entity_id=result.id,
            actor_user_id=user_id,
            request_id=request_id,
            before_state=before,
            after_state={"validation_status": result.validation_status.value, "mismatch_reason": mismatch_reason},
        )
        self.db.flush()
        return result
