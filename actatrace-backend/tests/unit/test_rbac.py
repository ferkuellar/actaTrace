from app.core.permissions import role_has_permission
from app.models.enums import UserRole


def test_ut_005_forbidden_role_rejected():
    assert role_has_permission(UserRole.CAPTURISTA, "acta:create") is True
    assert role_has_permission(UserRole.CAPTURISTA, "acta:approve") is False
    assert role_has_permission(UserRole.CIUDADANO_PUBLICO, "audit:read") is False

