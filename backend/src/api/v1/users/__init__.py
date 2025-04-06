"""
用户管理模块
提供用户相关的所有功能接口
"""
from .router import router
from .schemas import (
    UserCreate,
    UserUpdate,
    UserOut,
)
from .service import (
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user,
)

__all__ = [
    # 路由
    "router",
    
    # 数据模型
    "UserCreate",
    "UserUpdate",
    "UserOut",
    
    # 服务函数
    "create_user",
    "get_users",
    "get_user",
    "update_user",
    "delete_user",
] 