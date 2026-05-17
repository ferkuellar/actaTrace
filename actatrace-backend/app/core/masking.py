from typing import Any

SENSITIVE_KEYS = {
    "password",
    "hashed_password",
    "token",
    "access_token",
    "refresh_token",
    "jwt",
    "secret",
    "private_key",
    "storage_path",
    "storage_key",
    "storage_url",
}


def mask_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: ("***" if key.lower() in SENSITIVE_KEYS else mask_sensitive(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [mask_sensitive(item) for item in value]
    return value
