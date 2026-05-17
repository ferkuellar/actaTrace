from app.models.audit_log import AuditLog
from app.models.enums import UserRole
from app.tests.conftest import auth_headers, b64, create_polling_station, create_user


def test_acta_creation_creates_audit_log(client, db):
    create_user(db, UserRole.CAPTURISTA, "capturista@example.com")
    station = create_polling_station(db)

    doc_response = client.post(
        "/api/v1/documents/register-metadata",
            headers=auth_headers(client, "capturista@example.com"),
        json={
            "file_name": "acta.pdf",
            "file_type": "application/pdf",
            "file_size": 9,
            "storage_provider": "local-test",
            "storage_path": "tests/acta.pdf",
            "content_base64": b64(b"acta-data"),
        },
    )
    assert doc_response.status_code == 200, doc_response.text

    response = client.post(
        "/api/v1/actas",
        headers=auth_headers(client, "capturista@example.com"),
        json={
            "acta_code": "ACTA-2026-MXCMX-D12-S0456-B01",
            "polling_station_id": station.id,
            "document_id": doc_response.json()["id"],
            "election_type": "MUNICIPAL",
            "municipality": "Benito Juarez",
            "district": "D12",
            "section": "S0456",
            "expected_total_votes": 10,
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "UPLOADED"
    assert db.query(AuditLog).filter(AuditLog.action == "ACTA_CREATED").count() == 1
