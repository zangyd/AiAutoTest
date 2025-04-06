from fastapi import APIRouter
from src.api.base import api_router

# 创建v1版本路由
v1_router = APIRouter(prefix="/v1")

# 添加v1版本信息路由
@v1_router.get("/version")
async def get_version():
    return {
        "version": "1.0.0",
        "name": "API v1",
        "description": "API version 1"
    }

# 将v1路由添加到主路由
api_router.include_router(v1_router) 