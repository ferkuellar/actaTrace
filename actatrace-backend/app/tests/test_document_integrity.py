from app.blockchain.mock_provider import MockBlockchainProvider
from app.core.config import settings
from app.models.acta import Acta
from app.models.enums import ActaStatus, DocumentIntegrityStatus, UserRole
from app.services.blockchain_service import BlockchainService
from app.tests.conftest import auth_headers, create_polling_station, create_user


def _setup_uploaded_document(client, db, tmp_path, email="integrity@example.com", content=b"integrity"):
    settings.storage_provider = "local"
    settings.local_storage_path = str(tmp_path)
    user = create_user(db, UserRole.SUPERVISOR, email)
    station = create_polling_station(db)
    acta = Acta(
        acta_code="ACTA-2026-MXCMX-D12-S0456-B01",
        polling_station_id=station.id,
        status=ActaStatus.DRAFT,
        election_type="MUNICIPAL",
        municipality="Benito Juarez",
        district="D12",
        section="S0456",
        created_by=user.id,
    )
    db.add(acta)
    db.commit()
    db.refresh(acta)
    response = client.post(
        "/api/v1/documents/upload-acta",
        headers=auth_headers(client, email),
        data={"acta_id": acta.id, "polling_station_id": station.id, "document_type": "ACTA"},
        files={"file": ("acta.pdf", content, "application/pdf")},
    )
    assert response.status_code == 200, response.text
    return user, response.json()


def test_integrity_verification_success(client, db, tmp_path):
    _, document = _setup_uploaded_document(client, db, tmp_path)

    response = client.post(
        f"/api/v1/documents/{document['id']}/verify-integrity",
        headers=auth_headers(client, "integrity@example.com"),
    )

    assert response.status_code == 200
    assert response.json()["database_match"] is True
    assert response.json()["integrity_status"] == "VALID"


def test_integrity_mismatch_detection(client, db, tmp_path):
    _, document = _setup_uploaded_document(client, db, tmp_path, "mismatch@example.com", b"original")
    stored_file = tmp_path / document["storage_key"]
    stored_file.write_bytes(b"tampered")

    response = client.post(
        f"/api/v1/documents/{document['id']}/verify-integrity",
        headers=auth_headers(client, "mismatch@example.com"),
    )

    assert response.status_code == 200
    assert response.json()["database_match"] is False
    assert response.json()["integrity_status"] == "MISMATCH"


def test_missing_storage_object_detection(client, db, tmp_path):
    _, document = _setup_uploaded_document(client, db, tmp_path, "missing@example.com", b"missing")
    stored_file = tmp_path / document["storage_key"]
    stored_file.unlink()

    response = client.post(
        f"/api/v1/documents/{document['id']}/verify-integrity",
        headers=auth_headers(client, "missing@example.com"),
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_STORAGE_MISSING"


def test_blockchain_verification_mocked(client, db, tmp_path):
    user, document = _setup_uploaded_document(client, db, tmp_path, "blockchain-doc@example.com", b"anchored")
    anchor = BlockchainService(db, MockBlockchainProvider()).anchor_document_hash(document["id"], user.id, "req-test")
    db.commit()

    response = client.get(
        f"/api/v1/documents/{document['id']}/verify-blockchain",
        headers=auth_headers(client, "blockchain-doc@example.com"),
    )

    assert response.status_code == 200
    assert response.json()["blockchain_match"] is True
    assert response.json()["proof"]["exists"] is True
