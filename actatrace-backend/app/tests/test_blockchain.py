import pytest

from app.blockchain.exceptions import BlockchainHashAlreadyAnchored
from app.blockchain.mock_provider import MockBlockchainProvider
from app.blockchain.schemas import DocumentHashAnchorPayload
from app.core.errors import AppError
from app.models.audit_log import AuditLog
from app.models.blockchain_anchor import BlockchainAnchor
from app.models.document import Document
from app.models.enums import BlockchainVerificationStatus, DocumentIntegrityStatus, UserRole
from app.services.blockchain_service import BlockchainService
from app.services.blockchain_verification_service import generate_canonical_event_hash
from app.tests.conftest import auth_headers, b64, create_user
from app.models.mixins import utc_now


def _payload(hash_value: str = "a" * 64) -> DocumentHashAnchorPayload:
    return DocumentHashAnchorPayload(
        anchor_id="anchor-1",
        entity_type="DOCUMENT",
        entity_id="document-1",
        document_id="document-1",
        sha256_hash=hash_value,
        anchored_by="user-1",
        anchored_at=utc_now(),
        metadata_hash="b" * 64,
    )


def test_mock_provider_anchors_document_hash():
    provider = MockBlockchainProvider()
    payload = _payload("1" * 64)
    result = provider.anchor_document_hash(payload)
    assert result.transaction_id.startswith("mock-")
    assert result.status == "ANCHORED"


def test_mock_provider_verifies_existing_hash():
    provider = MockBlockchainProvider()
    payload = _payload("2" * 64)
    provider.anchor_document_hash(payload)
    result = provider.verify_hash(payload.sha256_hash)
    assert result.exists is True
    assert result.anchor_id == payload.anchor_id


def test_mock_provider_rejects_duplicate_hash():
    provider = MockBlockchainProvider()
    payload = _payload("3" * 64)
    provider.anchor_document_hash(payload)
    with pytest.raises(BlockchainHashAlreadyAnchored):
        provider.anchor_document_hash(payload)


def test_canonical_event_hash_is_deterministic():
    first = {"event_type": "RECEIVED", "acta_id": "a1", "performed_by": "u1"}
    second = {"performed_by": "u1", "event_type": "RECEIVED", "acta_id": "a1"}
    assert generate_canonical_event_hash(first) == generate_canonical_event_hash(second)


def test_blockchain_service_creates_anchor_record(db):
    user = create_user(db, UserRole.AUDITOR, "auditor@example.com")
    document = Document(
        file_name="acta.pdf",
        file_type="application/pdf",
        file_size=10,
        storage_provider="local-test",
        storage_path="tests/blockchain-acta.pdf",
        sha256_hash="4" * 64,
        uploaded_by=user.id,
        integrity_status=DocumentIntegrityStatus.VALID,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    anchor = BlockchainService(db, MockBlockchainProvider()).anchor_document_hash(document.id, user.id, "req-test")
    db.commit()

    assert anchor.verification_status == BlockchainVerificationStatus.ANCHORED
    assert db.query(AuditLog).filter(AuditLog.action == "BLOCKCHAIN_ANCHOR_CREATED").count() == 1


def test_blockchain_api_rejects_unauthorized_role(client, db):
    user = create_user(db, UserRole.CAPTURISTA, "capturista-blockchain@example.com")
    document = Document(
        file_name="acta.pdf",
        file_type="application/pdf",
        file_size=10,
        storage_provider="local-test",
        storage_path="tests/unauthorized-blockchain-acta.pdf",
        sha256_hash="5" * 64,
        uploaded_by=user.id,
        integrity_status=DocumentIntegrityStatus.VALID,
    )
    db.add(document)
    db.commit()

    response = client.post(
        f"/api/v1/blockchain/anchor/document/{document.id}",
        headers=auth_headers(client, "capturista-blockchain@example.com"),
    )
    assert response.status_code == 403


def test_blockchain_api_anchors_document_hash_successfully(client, db):
    user = create_user(db, UserRole.SUPERVISOR, "supervisor-api@example.com")
    doc_response = client.post(
        "/api/v1/documents/register-metadata",
        headers=auth_headers(client, "supervisor-api@example.com"),
        json={
            "file_name": "acta.pdf",
            "file_type": "application/pdf",
            "file_size": 9,
            "storage_provider": "local-test",
            "storage_path": "tests/api-blockchain-acta.pdf",
            "content_base64": b64(b"api-chain"),
        },
    )
    assert doc_response.status_code == 200, doc_response.text
    document_id = doc_response.json()["id"]

    response = client.post(
        f"/api/v1/blockchain/anchor/document/{document_id}",
        headers=auth_headers(client, "supervisor-api@example.com"),
    )
    assert response.status_code == 200, response.text
    assert response.json()["verification_status"] == "ANCHORED"


def test_blockchain_failure_creates_failed_anchor_and_audit_log(db):
    user = create_user(db, UserRole.AUDITOR, "auditor-failure@example.com")
    document = Document(
        file_name="acta.pdf",
        file_type="application/pdf",
        file_size=10,
        storage_provider="local-test",
        storage_path="tests/failing-blockchain-acta.pdf",
        sha256_hash="f" * 64,
        uploaded_by=user.id,
        integrity_status=DocumentIntegrityStatus.VALID,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    with pytest.raises(AppError):
        BlockchainService(db, MockBlockchainProvider()).anchor_document_hash(document.id, user.id, "req-fail")
    db.commit()

    anchor = db.query(BlockchainAnchor).filter(BlockchainAnchor.hash_value == "f" * 64).one()
    assert anchor.verification_status == BlockchainVerificationStatus.FAILED
    assert db.query(AuditLog).filter(AuditLog.action == "BLOCKCHAIN_ANCHOR_FAILED").count() == 1
