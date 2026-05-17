from app.services.hash_service import HashService


def test_sha256_generation():
    service = HashService()
    assert service.generate_sha256_from_bytes(b"actatrace") == "7bf8d7b33c85c73543e5b0579d3e188e33d3ecb66f1fb722187655f753b3a630"


def test_sha256_verify():
    service = HashService()
    digest = service.generate_sha256_from_bytes(b"acta")
    assert service.verify_sha256(b"acta", digest)
    assert not service.verify_sha256(b"tampered", digest)
