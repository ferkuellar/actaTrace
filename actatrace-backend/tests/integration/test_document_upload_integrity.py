from app.core.config import settings
from app.models.acta import Acta
from app.models.audit_log import AuditLog
from app.models.enums import ActaStatus, DocumentIntegrityStatus, UserRole
from app.services.document_integrity_service import DocumentIntegrityService
from app.storage.local_provider import LocalStorageProvider
from app.tests.conftest import auth_headers, create_polling_station, create_user


def _create_acta(db, user_id: str, station_id: str) -> Acta:
    acta = Acta(
        acta_code="ACTA-2026-CHH-D05-S0123-B02",
        polling_station_id=station_id,
        status=ActaStatus.DRAFT,
        election_type="MUNICIPAL",
        municipality="Juarez",
        district="D05",
        section="S0123",
        expected_total_votes=10,
        created_by=user_id,
    )
    db.add(acta)
    db.commit()
    db.refresh(acta)
    return acta


def test_it_002_upload_document_and_store_hash(client, db, tmp_path):
    settings.storage_provider = "local"
    settings.local_storage_path = str(tmp_path)
    user = create_user(db, UserRole.CAPTURISTA, "it-upload@example.com")
    station = create_polling_station(db)
    acta = _create_acta(db, user.id, station.id)
    response = client.post(
        "/api/v1/documents/upload-acta",
        headers=auth_headers(client, "it-upload@example.com"),
        data={"acta_id": acta.id, "polling_station_id": station.id, "document_type": "ACTA"},
        files={"file": ("acta.pdf", b"phase-10-evidence", "application/pdf")},
    )
    assert response.status_code == 200, response.text
    assert len(response.json()["sha256_hash"]) == 64


def test_it_004_detect_modified_document(client, db, tmp_path):
    settings.storage_provider = "local"
    settings.local_storage_path = str(tmp_path)
    user = create_user(db, UserRole.CAPTURISTA, "it-modified@example.com")
    station = create_polling_station(db)
    acta = _create_acta(db, user.id, station.id)
    upload = client.post(
        "/api/v1/documents/upload-acta",
        headers=auth_headers(client, "it-modified@example.com"),
        data={"acta_id": acta.id, "polling_station_id": station.id, "document_type": "ACTA"},
        files={"file": ("acta.pdf", b"original-evidence", "application/pdf")},
    )
    document_id = upload.json()["id"]
    document = db.get(__import__("app.models.document", fromlist=["Document"]).Document, document_id)
    LocalStorageProvider(str(tmp_path)).upload_file(b"modified-evidence", document.storage_key, document.mime_type)

    result = DocumentIntegrityService(db, LocalStorageProvider(str(tmp_path))).verify_integrity(document_id, user, "req-modified")
    db.commit()

    assert result["database_match"] is False
    assert db.get(type(document), document_id).integrity_status == DocumentIntegrityStatus.MISMATCH
    assert db.query(AuditLog).filter(AuditLog.action == "DOCUMENT_HASH_MISMATCH").count() == 1

