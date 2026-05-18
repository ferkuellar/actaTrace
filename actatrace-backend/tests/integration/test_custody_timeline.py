from app.models.acta import Acta
from app.models.custody_event import CustodyEvent
from app.models.enums import ActaStatus, CustodyEventType, UserRole
from app.models.mixins import utc_now
from app.tests.conftest import auth_headers, create_polling_station, create_user


def test_it_005_create_custody_event_and_timeline(client, db):
    user = create_user(db, UserRole.AUDITOR, "it-custody@example.com")
    station = create_polling_station(db)
    acta = Acta(acta_code="ACTA-2026-CHH-D05-S0123-B04", polling_station_id=station.id, status=ActaStatus.UPLOADED, election_type="MUNICIPAL", municipality=station.municipality, district=station.district, section=station.section, created_by=user.id)
    db.add(acta)
    db.flush()
    db.add(CustodyEvent(acta_id=acta.id, event_type=CustodyEventType.CREATED, performed_by=user.id, occurred_at=utc_now()))
    db.commit()
    response = client.get(f"/api/v1/traceability/actas/{acta.id}/timeline", headers=auth_headers(client, "it-custody@example.com"))
    assert response.status_code == 200, response.text
    assert any(item["event_type"] == "CUSTODY_CREATED" for item in response.json())

