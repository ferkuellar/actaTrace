from jose import jwt

from app.core.config import settings
from app.core.security import verify_password
from app.models.audit_log import AuditLog
from app.models.enums import AuditEventCategory, UserRole, UserStatus
from app.tests.conftest import auth_headers, create_user


def test_login_jwt_contains_required_claims(client, db):
    user = create_user(db, UserRole.AUDITOR)
    response = client.post("/api/v1/auth/login", json={"email": user.email, "password": "StrongPassword123"})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )
    assert payload["sub"] == user.id
    assert payload["email"] == user.email
    assert payload["role"] == UserRole.AUDITOR
    assert payload["organization"] == user.organization
    assert payload["status"] == UserStatus.ACTIVE
    assert payload["iss"] == settings.jwt_issuer
    assert payload["aud"] == settings.jwt_audience
    assert "iat" in payload
    assert "exp" in payload


def test_failed_login_creates_security_audit_event(client, db):
    user = create_user(db, UserRole.AUDITOR)
    response = client.post("/api/v1/auth/login", json={"email": user.email, "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_INVALID_CREDENTIALS"
    log = db.query(AuditLog).filter(AuditLog.action == "AUTH_LOGIN_FAILED").one()
    assert log.event_category == AuditEventCategory.SECURITY
    assert log.metadata_json["reason"] == "invalid_credentials"


def test_disabled_account_cannot_login(client, db):
    user = create_user(db, UserRole.AUDITOR)
    user.status = UserStatus.SUSPENDED
    db.commit()
    response = client.post("/api/v1/auth/login", json={"email": user.email, "password": "StrongPassword123"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_ACCOUNT_DISABLED"


def test_invalid_token_rejected(client):
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_TOKEN_INVALID"


def test_auth_me_and_logout(client, db):
    user = create_user(db, UserRole.AUDITOR)
    headers = auth_headers(client, user.email)
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == user.email
    logout_response = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 200
    assert db.query(AuditLog).filter(AuditLog.action == "AUTH_LOGOUT").count() == 1


def test_security_headers_present(client):
    response = client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "default-src 'none'" in response.headers["content-security-policy"]


def test_role_protected_endpoint_records_forbidden(client, db):
    user = create_user(db, UserRole.CAPTURISTA)
    response = client.get("/api/v1/users", headers=auth_headers(client, user.email))
    assert response.status_code == 403
    assert db.query(AuditLog).filter(AuditLog.action == "AUTH_FORBIDDEN").count() == 1


def test_public_endpoint_does_not_require_auth(client):
    response = client.get("/api/v1/traceability/public/actas/UNKNOWN")
    assert response.status_code == 404


def test_rate_limit_exceeded_returns_structured_error(client):
    for _ in range(settings.rate_limit_login_per_minute):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "none@example.com", "password": "wrong"},
            headers={"x-test-rate-limit": "true"},
        )
        assert response.status_code == 401
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "none@example.com", "password": "wrong"},
        headers={"x-test-rate-limit": "true"},
    )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "SECURITY_RATE_LIMIT_EXCEEDED"


def test_password_is_hashed(db):
    user = create_user(db, UserRole.AUDITOR)
    assert user.hashed_password != "StrongPassword123"
    assert verify_password("StrongPassword123", user.hashed_password)
