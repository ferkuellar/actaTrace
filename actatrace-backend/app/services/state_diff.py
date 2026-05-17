from datetime import date, datetime
from enum import Enum
from typing import Any

from app.core.masking import SENSITIVE_KEYS, mask_sensitive



def _safe_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return mask_sensitive({key: _safe_value(item) for key, item in value.items()})
    if isinstance(value, list):
        return [_safe_value(item) for item in value]
    return value


def capture_state(entity: Any) -> dict[str, Any]:
    if entity is None:
        return {}
    columns = getattr(entity, "__table__", None)
    if columns is None:
        return {}
    state: dict[str, Any] = {}
    for column in entity.__table__.columns:
        key = column.name
        if key.lower() in SENSITIVE_KEYS:
            state[key] = "***"
        else:
            state[key] = _safe_value(getattr(entity, key))
    return state


def diff_states(before: dict[str, Any] | None, after: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    before = before or {}
    after = after or {}
    changed: dict[str, dict[str, Any]] = {}
    for key in sorted(set(before) | set(after)):
        if key.lower() in SENSITIVE_KEYS:
            continue
        if before.get(key) != after.get(key):
            changed[key] = {"before": _safe_value(before.get(key)), "after": _safe_value(after.get(key))}
    return changed
