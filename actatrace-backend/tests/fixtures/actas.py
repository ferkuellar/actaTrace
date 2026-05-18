from app.models.acta import Acta
from app.models.enums import ActaStatus


def create_test_acta(db, user_id: str, polling_station, *, code_suffix: str = "B01", expected_total_votes: int = 100) -> Acta:
    acta = Acta(
        acta_code=f"ACTA-2026-CHH-D05-S0123-{code_suffix}",
        polling_station_id=polling_station.id,
        status=ActaStatus.DRAFT,
        election_type="MUNICIPAL",
        municipality=polling_station.municipality,
        district=polling_station.district,
        section=polling_station.section,
        expected_total_votes=expected_total_votes,
        created_by=user_id,
    )
    db.add(acta)
    db.commit()
    db.refresh(acta)
    return acta

