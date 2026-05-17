from app.core.permissions import role_has_permission
from app.models.enums import UserRole


class PermissionService:
    def is_allowed(self, role: UserRole, permission: str) -> bool:
        return role_has_permission(role, permission)
