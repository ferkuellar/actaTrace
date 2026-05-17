from app.models.enums import UserRole

ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.ADMIN_ELECTORAL: {"*"},
    UserRole.CAPTURISTA: {"acta:create", "document:create", "prep:create", "own:read"},
    UserRole.SUPERVISOR: {"acta:review", "acta:approve", "custody:validate", "alert:manage", "blockchain:anchor"},
    UserRole.AUDITOR: {"audit:read", "traceability:read", "forensic:read", "alert:read", "proof:read"},
    UserRole.OBSERVADOR: {"traceability:read", "dashboard:read"},
    UserRole.CIUDADANO_PUBLICO: {"public:read"},
}


def role_has_permission(role: UserRole, permission: str) -> bool:
    permissions = ROLE_PERMISSIONS.get(role, set())
    return "*" in permissions or permission in permissions
