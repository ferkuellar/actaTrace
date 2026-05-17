from app.storage.local_provider import LocalStorageProvider


def test_local_storage_provider_round_trip(tmp_path):
    provider = LocalStorageProvider(str(tmp_path))
    result = provider.upload_file(b"acta", "actas/2026/test.pdf", "application/pdf")

    assert result.object_key == "actas/2026/test.pdf"
    assert provider.file_exists(result.object_key)
    assert provider.get_file(result.object_key) == b"acta"
    assert provider.generate_presigned_url(result.object_key, 300).startswith("local://")


def test_local_storage_provider_delete(tmp_path):
    provider = LocalStorageProvider(str(tmp_path))
    provider.upload_file(b"acta", "actas/delete.pdf", "application/pdf")
    assert provider.delete_file("actas/delete.pdf") is True
    assert provider.file_exists("actas/delete.pdf") is False
