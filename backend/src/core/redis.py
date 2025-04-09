"""
Redis连接管理模块
"""
import redis
from core.config.settings import settings
from core.logging import logger

def get_redis() -> redis.Redis:
    """
    获取Redis连接
    """
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        redis_client.ping()  # 测试连接
        logger.info(f"Redis连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        return redis_client
    except Exception as e:
        logger.error(f"Redis连接失败: {str(e)}")
        raise 