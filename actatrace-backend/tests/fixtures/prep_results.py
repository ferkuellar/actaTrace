from app.models.mixins import utc_now
from app.models.prep_result import PREPResult


def create_test_prep_result(db, acta_id: str, polling_station_id: str, user_id: str, *, total_votes: int = 100) -> PREPResult:
    prep = PREPResult(
        acta_id=acta_id,
        polling_station_id=polling_station_id,
        captured_by=user_id,
        candidate_results={"candidate_a": total_votes - 10, "candidate_b": 10},
        total_votes=total_votes,
        null_votes=0,
        valid_votes=total_votes,
        captured_at=utc_now(),
    )
    db.add(prep)
    db.commit()
    db.refresh(prep)
    return prep
