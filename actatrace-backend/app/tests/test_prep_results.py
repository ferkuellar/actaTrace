from datetime import datetime, timezone

from app.models.acta import Acta
from app.models.enums import ActaStatus, PREPValidationStatus, UserRole
from app.tests.conftest import auth_headers, create_polling_station, create_user


def test_prep_validation_basic_match(client, db):
    capturista = create_user(db, UserRole.CAPTURISTA, "capturista@example.com")
    supervisor = create_user(db, UserRole.SUPERVISOR, "supervisor@example.com")
    station = create_polling_station(db)
    acta = Acta(
        acta_code="ACTA-2026-MXCMX-D12-S0456-B01",
        polling_station_id=station.id,
        status=ActaStatus.DRAFT,
        election_type="MUNICIPAL",
        municipality="Benito Juarez",
        district="D12",
        section="S0456",
        expected_total_votes=10,
        created_by=capturista.id,
    )
    db.add(acta)
    db.commit()
    db.refresh(acta)

    create_response = client.post(
        "/api/v1/prep-results",
        headers=auth_headers(client, "capturista@example.com"),
        json={
            "acta_id": acta.id,
            "polling_station_id": station.id,
            "candidate_results": {"PARTY_A": 6, "PARTY_B": 2},
            "total_votes": 10,
            "null_votes": 2,
            "valid_votes": 8,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert create_response.status_code == 200, create_response.text

    prep_id = create_response.json()["id"]
    validate_response = client.post(
        f"/api/v1/prep-results/{prep_id}/validate",
        headers=auth_headers(client, "supervisor@example.com"),
    )
    assert validate_response.status_code == 200, validate_response.text
    assert validate_response.json()["validation_status"] == PREPValidationStatus.MATCHED.value
