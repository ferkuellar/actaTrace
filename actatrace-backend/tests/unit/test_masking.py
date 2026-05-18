from app.core.masking import mask_sensitive


def test_ut_006_sensitive_fields_masked_from_audit_state():
    masked = mask_sensitive({"email": "user@example.com", "access_token": "secret", "nested": {"password": "secret"}})
    assert masked["email"] == "user@example.com"
    assert masked["access_token"] == "***"
    assert masked["nested"]["password"] == "***"

