from app.models.document import Document
from app.models.enums import DocumentAccessStatus, DocumentIntegrityStatus, DocumentLifecycleStatus


def create_test_document(db, user_id: str, *, sha256_hash: str = "a" * 64, storage_key: str = "actas/test/doc.pdf") -> Document:
    document = Document(
        file_name="acta.pdf",
        original_file_name="acta-original.pdf",
        file_type="application/pdf",
        mime_type="application/pdf",
        file_size=128,
        storage_provider="local",
        storage_path=storage_key,
        storage_key=storage_key,
        sha256_hash=sha256_hash,
        uploaded_by=user_id,
        integrity_status=DocumentIntegrityStatus.VALID,
        access_status=DocumentAccessStatus.PRIVATE,
        lifecycle_status=DocumentLifecycleStatus.STORED,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

