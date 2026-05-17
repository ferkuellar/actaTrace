import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID


VOLATILE_FIELDS = {
    "created_at",
    "updated_at",
    "request_id",
    "ip_address",
    "user_agent",
}


def _canonical_default(value):
    if isinstance(value, datetime):
        return value.astimezone().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def canonicalize_payload(payload: dict) -> dict:
    return {key: value for key, value in payload.items() if key not in VOLATILE_FIELDS}


def generate_canonical_event_hash(payload: dict) -> str:
    canonical_payload = canonicalize_payload(payload)
    encoded = json.dumps(
        canonical_payload,
        sort_keys=True,
        separators=(",", ":"),
        default=_canonical_default,
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
