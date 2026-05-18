from app.models.audit_log import AuditLog
from app.models.enums import UserRole
from app.tests.conftest import create_user


def test_st_006_failed_login_creates_audit_event(client, db):
    create_user(db, UserRole.ADMIN_ELECTORAL, "security-admin@example.com")
    response = client.post("/api/v1/auth/login", json={"email": "security-admin@example.com", "password": "wrong-password"})
    assert response.status_code == 401
    assert db.query(AuditLog).filter(AuditLog.action == "AUTH_LOGIN_FAILED").count() == 1


def test_login_success(client, db):
    create_user(db, UserRole.ADMIN_ELECTORAL, "security-success@example.com")
    response = client.post("/api/v1/auth/login", json={"email": "security-success@example.com", "password": "StrongPassword123"})
    assert response.status_code == 200
    assert response.json()["access_token"]

