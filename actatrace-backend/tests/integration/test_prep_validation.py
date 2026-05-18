from app.models.acta import Acta
from app.models.enums import ActaStatus, AlertType, PREPValidationStatus, UserRole
from app.models.mixins import utc_now
from app.models.prep_result import PREPResult
from app.services.inconsistency_detection_service import InconsistencyDetectionService
from app.tests.conftest import create_polling_station, create_user


def test_it_007_detect_prep_mismatch(db):
    user = create_user(db, UserRole.AUDITOR, "it-prep@example.com")
    station = create_polling_station(db)
    acta = Acta(
        acta_code="ACTA-2026-CHH-D05-S0123-B03",
        polling_station_id=station.id,
        status=ActaStatus.UNDER_REVIEW,
        election_type="MUNICIPAL",
        municipality=station.municipality,
        district=station.district,
        section=station.section,
        expected_total_votes=100,
        created_by=user.id,
    )
    db.add(acta)
    db.flush()
    db.add(
        PREPResult(
            acta_id=acta.id,
            polling_station_id=station.id,
            captured_by=user.id,
            candidate_results={"A": 40},
            total_votes=40,
            null_votes=0,
            valid_votes=40,
            captured_at=utc_now(),
            validation_status=PREPValidationStatus.MISMATCHED,
        )
    )
    db.commit()

    alerts = InconsistencyDetectionService(db).detect_for_acta(acta.id)
    assert any(alert.alert_type == AlertType.PREP_ACTA_MISMATCH for alert in alerts)
