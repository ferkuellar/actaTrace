from datetime import datetime, timezone

from app.core.config import settings
from app.models.enums import UserRole
from app.tests.conftest import auth_headers, create_polling_station, create_user


def test_e2e_full_acta_verification_flow(client, db, tmp_path):
    settings.storage_provider = "local"
    settings.local_storage_path = str(tmp_path)
    create_user(db, UserRole.CAPTURISTA, "e2e-capturista@example.com")
    create_user(db, UserRole.SUPERVISOR, "e2e-supervisor@example.com")
    create_user(db, UserRole.AUDITOR, "e2e-auditor@example.com")
    station = create_polling_station(db)

    acta_response = client.post(
        "/api/v1/actas",
        headers=auth_headers(client, "e2e-capturista@example.com"),
        json={
            "acta_code": "ACTA-2026-CHH-D05-S0123-E2E",
            "polling_station_id": station.id,
            "election_type": "MUNICIPAL",
            "municipality": station.municipality,
            "district": station.district,
            "section": station.section,
            "expected_total_votes": 100,
        },
    )
    assert acta_response.status_code == 200, acta_response.text
    acta_id = acta_response.json()["id"]

    upload_response = client.post(
        "/api/v1/documents/upload-acta",
        headers=auth_headers(client, "e2e-capturista@example.com"),
        data={"acta_id": acta_id, "polling_station_id": station.id, "document_type": "ACTA"},
        files={"file": ("acta.pdf", b"e2e-acta-document", "application/pdf")},
    )
    assert upload_response.status_code == 200, upload_response.text
    document_id = upload_response.json()["id"]

    anchor_response = client.post(
        f"/api/v1/blockchain/anchor/document/{document_id}",
        headers=auth_headers(client, "e2e-supervisor@example.com"),
    )
    assert anchor_response.status_code == 200, anchor_response.text

    prep_response = client.post(
        "/api/v1/prep-results",
        headers=auth_headers(client, "e2e-capturista@example.com"),
        json={
            "acta_id": acta_id,
            "polling_station_id": station.id,
            "candidate_results": {"candidate_a": 90, "candidate_b": 10},
            "total_votes": 100,
            "null_votes": 0,
            "valid_votes": 100,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert prep_response.status_code == 200, prep_response.text
    prep_id = prep_response.json()["id"]

    validate_response = client.post(
        f"/api/v1/prep-results/{prep_id}/validate",
        headers=auth_headers(client, "e2e-supervisor@example.com"),
    )
    assert validate_response.status_code == 200, validate_response.text

    timeline_response = client.get(
        f"/api/v1/traceability/actas/{acta_id}/timeline",
        headers=auth_headers(client, "e2e-auditor@example.com"),
    )
    assert timeline_response.status_code == 200, timeline_response.text
    assert timeline_response.json()

    report_response = client.get(
        f"/api/v1/traceability/actas/{acta_id}/forensic-report",
        headers=auth_headers(client, "e2e-auditor@example.com"),
    )
    assert report_response.status_code == 200, report_response.text
    assert report_response.json()["acta"]["id"] == acta_id

    public_response = client.get(f"/api/v1/traceability/public/actas/{acta_response.json()['acta_code']}")
    assert public_response.status_code == 200, public_response.text
    assert "ip_address" not in public_response.text
