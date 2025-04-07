"""Redis数据库连接模块"""
from typing import AsyncGenerator
import redis.asyncio as redis
from fastapi import Depends

from core.config import settings


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """
    获取Redis数据库连接
    
    Yields:
        redis.Redis: Redis客户端
    """
    # 创建Redis连接
    try:
        conn = redis.from_url(
            settings.REDIS_URI,
            encoding="utf-8",
            decode_responses=True
        )
        yield conn
    finally:
        # 关闭连接
        try:
            await conn.close()
        except Exception:
            pass 