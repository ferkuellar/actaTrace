from app.models.enums import UserRole
from app.tests.conftest import auth_headers, create_user


def test_rbac_forbidden_access_for_capturista_on_users(client, db):
    create_user(db, UserRole.CAPTURISTA, "capturista@example.com")
    response = client.get("/api/v1/users", headers=auth_headers(client, "capturista@example.com"))
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "RBAC_FORBIDDEN"
