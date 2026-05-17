import hashlib
import json
from typing import Any

from app.core.masking import mask_sensitive


VOLATILE_FIELDS = {"id", "created_at", "updated_at", "request_id"}


class AuditHashChainService:
    @staticmethod
    def canonical_event_hash(payload: dict[str, Any]) -> str:
        stable_payload = {key: value for key, value in payload.items() if key not in VOLATILE_FIELDS}
        encoded = json.dumps(mask_sensitive(stable_payload), sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def chain_hash(event_hash: str, previous_event_hash: str | None) -> str:
        material = f"{previous_event_hash or ''}:{event_hash}".encode("utf-8")
        return hashlib.sha256(material).hexdigest()
