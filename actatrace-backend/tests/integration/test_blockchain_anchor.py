from app.models.document import Document
from app.models.enums import DocumentIntegrityStatus, UserRole
from app.services.blockchain_service import BlockchainService
from app.tests.conftest import create_user


def test_it_008_anchor_document_hash_to_mock_blockchain(db):
    user = create_user(db, UserRole.AUDITOR, "it-chain@example.com")
    document = Document(file_name="acta.pdf", file_type="application/pdf", file_size=8, storage_provider="local", storage_path="actas/it-chain.pdf", sha256_hash="b" * 64, uploaded_by=user.id, integrity_status=DocumentIntegrityStatus.VALID)
    db.add(document)
    db.commit()
    anchor = BlockchainService(db).anchor_document_hash(document.id, user.id, "req-chain")
    db.commit()
    assert anchor.transaction_hash.startswith("mock-")

