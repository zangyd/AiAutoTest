"""Redis数据库连接模块"""
import redis
from core.config.settings import settings
import logging

logger = logging.getLogger(__name__)

_redis_client = None

def get_redis():
    """获取Redis客户端实例
    
    Returns:
        redis.Redis: Redis客户端实例
    """
    global _redis_client
    
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
                encoding='utf-8'
            )
            logger.info(f"Redis连接已建立 - {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
            raise
    
    return _redis_client 