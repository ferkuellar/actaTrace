from app.models.enums import UserRole
from app.tests.conftest import create_user


def test_st_008_rate_limit_returns_safe_error(client, db):
    create_user(db, UserRole.ADMIN_ELECTORAL, "rate-limit@example.com")
    for _ in range(6):
        response = client.post(
            "/api/v1/auth/login",
            headers={"x-test-rate-limit": "true"},
            json={"email": "rate-limit@example.com", "password": "wrong-password"},
        )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "SECURITY_RATE_LIMIT_EXCEEDED"
    assert "password" not in response.text.lower()

