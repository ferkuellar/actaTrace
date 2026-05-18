from app.services.state_diff import diff_states


def test_audit_diff_excludes_sensitive_fields():
    diff = diff_states(
        {"status": "DRAFT", "password": "old-secret"},
        {"status": "VERIFIED", "password": "new-secret"},
    )
    assert diff["status"] == {"before": "DRAFT", "after": "VERIFIED"}
    assert "password" not in diff

