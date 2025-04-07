"""
API模块初始化文件

提供API相关的路由注册和版本管理
"""

from fastapi import APIRouter
from .v1 import router as v1_router

# 创建API主路由
api_router = APIRouter()

# 注册v1版本路由
api_router.include_router(v1_router, prefix="/v1")

__all__ = ["api_router"] 