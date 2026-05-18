from app.services.document_storage_service import DocumentStorageService


def test_ut_008_object_key_generated_safely(db):
    key = DocumentStorageService(db).generate_object_key(
        election_year=2026,
        state="Chihuahua / Norte",
        municipality="Juarez Centro",
        polling_station_code="../CHH-D05-S0123",
        acta_id="acta id",
        document_id="document id",
        extension=".pdf",
    )
    assert key.startswith("actas/2026/")
    assert ".." not in key
    assert " " not in key
