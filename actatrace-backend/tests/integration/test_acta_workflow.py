from app.models.audit_log import AuditLog
from app.models.enums import UserRole
from app.tests.conftest import auth_headers, create_polling_station, create_user


def test_it_001_create_acta_successfully(client, db):
    user = create_user(db, UserRole.CAPTURISTA, "it-acta@example.com")
    station = create_polling_station(db)
    response = client.post(
        "/api/v1/actas",
        headers=auth_headers(client, "it-acta@example.com"),
        json={
            "acta_code": "ACTA-2026-CHH-D05-S0123-B01",
            "polling_station_id": station.id,
            "election_type": "MUNICIPAL",
            "municipality": "Juarez",
            "district": "D05",
            "section": "S0123",
            "expected_total_votes": 100,
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["acta_code"] == "ACTA-2026-CHH-D05-S0123-B01"
    assert db.query(AuditLog).filter(AuditLog.action == "ACTA_CREATED").count() == 1

