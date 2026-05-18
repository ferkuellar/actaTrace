from app.models.audit_log import AuditLog
from app.models.enums import UserRole
from app.tests.conftest import auth_headers, create_user


def test_st_001_admin_can_manage_users(client, db):
    create_user(db, UserRole.ADMIN_ELECTORAL, "matrix-admin@example.com")
    response = client.get("/api/v1/users", headers=auth_headers(client, "matrix-admin@example.com"))
    assert response.status_code == 200


def test_st_002_capturista_cannot_approve_acta(client, db):
    create_user(db, UserRole.CAPTURISTA, "matrix-capturista@example.com")
    response = client.post("/api/v1/actas/not-real/approve", headers=auth_headers(client, "matrix-capturista@example.com"))
    assert response.status_code == 403
    assert db.query(AuditLog).filter(AuditLog.action == "AUTH_FORBIDDEN").count() == 1


def test_st_004_public_user_cannot_access_admin_endpoint(client, db):
    create_user(db, UserRole.CIUDADANO_PUBLICO, "matrix-public@example.com")
    response = client.get("/api/v1/users", headers=auth_headers(client, "matrix-public@example.com"))
    assert response.status_code == 403

