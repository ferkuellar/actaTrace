import pytest

from app.core.errors import AppError
from app.services.blockchain_service import BlockchainService
from app.services.blockchain_verification_service import generate_canonical_event_hash


def test_ut_003_canonical_json_hash_is_deterministic():
    first = {"event_type": "RECEIVED", "acta_id": "a1", "performed_by": "u1"}
    second = {"performed_by": "u1", "acta_id": "a1", "event_type": "RECEIVED"}
    assert generate_canonical_event_hash(first) == generate_canonical_event_hash(second)


def test_ut_004_invalid_sha256_format_rejected(db):
    with pytest.raises(AppError):
        BlockchainService(db)._ensure_valid_hash("not-a-valid-hash")

