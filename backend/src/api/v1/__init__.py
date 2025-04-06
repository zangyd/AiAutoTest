"""
API v1版本路由注册
"""
from fastapi import APIRouter
from .auth import router as auth_router
# from .users import router as users_router  # 用户模块待实现

# 创建API主路由
api_router = APIRouter(prefix="/api")

# 创建v1版本路由
router = APIRouter(prefix="/v1")

# 添加v1版本信息路由
@router.get("/version")
async def get_version():
    return {
        "version": "1.0.0",
        "name": "API v1",
        "description": "API version 1"
    }

# 注册认证路由
router.include_router(auth_router)

# 注册用户路由
# router.include_router(users_router)  # 用户模块待实现

# 将v1路由添加到主路由
api_router.include_router(router)

# 导出主路由
__all__ = ["api_router"] 