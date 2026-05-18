from app.models.enums import UserRole
from app.tests.conftest import create_user


def create_phase10_users(db):
    return {
        "admin": create_user(db, UserRole.ADMIN_ELECTORAL, "phase10-admin@example.com"),
        "capturista": create_user(db, UserRole.CAPTURISTA, "phase10-capturista@example.com"),
        "supervisor": create_user(db, UserRole.SUPERVISOR, "phase10-supervisor@example.com"),
        "auditor": create_user(db, UserRole.AUDITOR, "phase10-auditor@example.com"),
        "observador": create_user(db, UserRole.OBSERVADOR, "phase10-observador@example.com"),
        "public": create_user(db, UserRole.CIUDADANO_PUBLICO, "phase10-public@example.com"),
    }

