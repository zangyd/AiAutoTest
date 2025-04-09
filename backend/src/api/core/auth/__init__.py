"""
认证模块

重导出核心认证功能
"""
from core.auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from core.auth.permissions import (
    PermissionService,
    require_permission,
    require_any_permission,
    require_all_permissions,
)

# 从core.auth.dependencies中导入get_current_user函数
from core.auth.dependencies import get_current_user

__all__ = [
    'create_access_token',
    'create_refresh_token',
    'verify_token',
    'PermissionService',
    'require_permission',
    'require_any_permission',
    'require_all_permissions',
    'get_current_user',
] 