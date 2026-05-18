from io import BytesIO

from app.services.hash_service import HashService


def test_ut_001_sha256_hash_is_deterministic():
    service = HashService()
    content = b"phase-10-acta-evidence"
    assert service.generate_sha256_from_bytes(content) == service.generate_sha256_from_bytes(content)


def test_ut_002_modified_file_produces_different_hash():
    service = HashService()
    assert service.generate_sha256_from_bytes(b"original") != service.generate_sha256_from_bytes(b"modified")


def test_sha256_stream_preserves_stream_position():
    service = HashService()
    stream = BytesIO(b"streamed-acta")
    assert service.generate_sha256_from_stream(stream) == service.generate_sha256_from_bytes(b"streamed-acta")
    assert stream.tell() == 0

