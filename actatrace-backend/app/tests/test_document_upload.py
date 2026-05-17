from app.core.config import settings
from app.models.acta import Acta
from app.models.audit_log import AuditLog
from app.models.document import Document
from app.models.enums import ActaStatus, DocumentAccessStatus, UserRole
from app.tests.conftest import auth_headers, create_polling_station, create_user


def _create_acta(db, user_id: str, station_id: str, suffix: str = "B01") -> Acta:
    acta = Acta(
        acta_code=f"ACTA-2026-MXCMX-D12-S0456-{suffix}",
        polling_station_id=station_id,
        status=ActaStatus.DRAFT,
        election_type="MUNICIPAL",
        municipality="Benito Juarez",
        district="D12",
        section="S0456",
        expected_total_votes=10,
        created_by=user_id,
    )
    db.add(acta)
    db.commit()
    db.refresh(acta)
    return acta


def _set_local_storage(tmp_path):
    settings.storage_provider = "local"
    settings.local_storage_path = str(tmp_path)


def test_successful_document_upload(client, db, tmp_path):
    _set_local_storage(tmp_path)
    user = create_user(db, UserRole.CAPTURISTA, "upload@example.com")
    station = create_polling_station(db)
    acta = _create_acta(db, user.id, station.id)

    response = client.post(
        "/api/v1/documents/upload-acta",
        headers=auth_headers(client, "upload@example.com"),
        data={"acta_id": acta.id, "polling_station_id": station.id, "document_type": "ACTA", "notes": "test upload"},
        files={"file": ("acta.pdf", b"acta-upload", "application/pdf")},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["sha256_hash"]
    assert body["storage_key"].startswith("actas/2026/")
    assert db.get(Acta, acta.id).document_id == body["id"]
    assert db.query(AuditLog).filter(AuditLog.action == "DOCUMENT_UPLOADED").count() == 1


def test_invalid_file_type_rejected(client, db, tmp_path):
    _set_local_storage(tmp_path)
    user = create_user(db, UserRole.CAPTURISTA, "invalid-type@example.com")
    station = create_polling_station(db)
    acta = _create_acta(db, user.id, station.id)

    response = client.post(
        "/api/v1/documents/upload-acta",
        headers=auth_headers(client, "invalid-type@example.com"),
        data={"acta_id": acta.id, "polling_station_id": station.id, "document_type": "ACTA"},
        files={"file": ("acta.exe", b"not-allowed", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "DOCUMENT_INVALID_FILE_TYPE"


def test_oversized_file_rejected(client, db, tmp_path):
    _set_local_storage(tmp_path)
    settings.max_document_upload_mb = 0
    user = create_user(db, UserRole.CAPTURISTA, "oversized@example.com")
    station = create_polling_station(db)
    acta = _create_acta(db, user.id, station.id)

    response = client.post(
        "/api/v1/documents/upload-acta",
        headers=auth_headers(client, "oversized@example.com"),
        data={"acta_id": acta.id, "polling_station_id": station.id, "document_type": "ACTA"},
        files={"file": ("acta.pdf", b"x", "application/pdf")},
    )
    settings.max_document_upload_mb = 25

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "DOCUMENT_FILE_TOO_LARGE"


def test_duplicate_document_hash_rejected(client, db, tmp_path):
    _set_local_storage(tmp_path)
    user = create_user(db, UserRole.CAPTURISTA, "duplicate@example.com")
    station = create_polling_station(db)
    acta = _create_acta(db, user.id, station.id)

    payload = {
        "headers": auth_headers(client, "duplicate@example.com"),
        "data": {"acta_id": acta.id, "polling_station_id": station.id, "document_type": "ACTA"},
        "files": {"file": ("acta.pdf", b"same-content", "application/pdf")},
    }
    assert client.post("/api/v1/documents/upload-acta", **payload).status_code == 200
    acta2 = _create_acta(db, user.id, station.id, "B02")
    payload["data"]["acta_id"] = acta2.id
    response = client.post("/api/v1/documents/upload-acta", **payload)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DOCUMENT_HASH_ALREADY_EXISTS"


def test_document_metadata_retrieval(client, db, tmp_path):
    _set_local_storage(tmp_path)
    user = create_user(db, UserRole.CAPTURISTA, "metadata@example.com")
    station = create_polling_station(db)
    acta = _create_acta(db, user.id, station.id)
    upload = client.post(
        "/api/v1/documents/upload-acta",
        headers=auth_headers(client, "metadata@example.com"),
        data={"acta_id": acta.id, "polling_station_id": station.id, "document_type": "ACTA"},
        files={"file": ("acta.pdf", b"metadata", "application/pdf")},
    )
    document_id = upload.json()["id"]

    response = client.get(f"/api/v1/documents/{document_id}", headers=auth_headers(client, "metadata@example.com"))

    assert response.status_code == 200
    assert response.json()["id"] == document_id


def test_unauthorized_download_rejected(client, db, tmp_path):
    _set_local_storage(tmp_path)
    uploader = create_user(db, UserRole.CAPTURISTA, "private-uploader@example.com")
    public_user = create_user(db, UserRole.CIUDADANO_PUBLICO, "public-private@example.com")
    station = create_polling_station(db)
    acta = _create_acta(db, uploader.id, station.id)
    upload = client.post(
        "/api/v1/documents/upload-acta",
        headers=auth_headers(client, "private-uploader@example.com"),
        data={"acta_id": acta.id, "polling_station_id": station.id, "document_type": "ACTA"},
        files={"file": ("acta.pdf", b"private", "application/pdf")},
    )

    response = client.get(
        f"/api/v1/documents/{upload.json()['id']}/download",
        headers=auth_headers(client, "public-private@example.com"),
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "DOCUMENT_ACCESS_DENIED"


def test_public_document_download_allowed_when_public_verifiable(client, db, tmp_path):
    _set_local_storage(tmp_path)
    uploader = create_user(db, UserRole.CAPTURISTA, "public-uploader@example.com")
    create_user(db, UserRole.CIUDADANO_PUBLICO, "public-viewer@example.com")
    station = create_polling_station(db)
    acta = _create_acta(db, uploader.id, station.id)
    upload = client.post(
        "/api/v1/documents/upload-acta",
        headers=auth_headers(client, "public-uploader@example.com"),
        data={"acta_id": acta.id, "polling_station_id": station.id, "document_type": "ACTA"},
        files={"file": ("acta.pdf", b"public", "application/pdf")},
    )
    document = db.get(Document, upload.json()["id"])
    document.access_status = DocumentAccessStatus.PUBLIC_VERIFIABLE
    db.commit()

    response = client.get(
        f"/api/v1/documents/{document.id}/download",
        headers=auth_headers(client, "public-viewer@example.com"),
    )

    assert response.status_code == 200
    assert response.json()["download_url"].startswith("local://")
