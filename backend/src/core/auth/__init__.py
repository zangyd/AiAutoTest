"""
认证模块

负责系统的认证相关功能:
- JWT认证
- 权限管理
- 用户认证
- 会话管理
"""
from .models import User, Role, Permission, Department, LoginLog, OperationLog
from .schemas import TokenResponse, UserLogin, RefreshToken, UserOut

# 避免循环导入，将这些导入移到需要的地方
# from .jwt import create_access_token, create_refresh_token, verify_token, get_current_user
# from .dependencies import get_current_active_user, get_current_superuser, check_permissions
# from .service import AuthService

__all__ = [
    "User", "Role", "Permission", "Department", "LoginLog", "OperationLog",
    "TokenResponse", "UserLogin", "RefreshToken", "UserOut"
] 