"""Redis连接管理器
提供Redis连接池和重试机制
"""
import redis
from redis.connection import ConnectionPool
from redis.exceptions import ConnectionError, RedisError
import logging
import time
from typing import Optional, Any, Dict, Union, List
import json
import asyncio
from core.config import settings

logger = logging.getLogger(__name__)

class RedisManager:
    """Redis连接管理器"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._create_pool()
        
    def _create_pool(self):
        """创建连接池"""
        try:
            self._pool = ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                max_connections=100,
                health_check_interval=30
            )
            logger.info("Redis连接池初始化成功")
        except Exception as e:
            logger.error(f"Redis连接池初始化失败: {str(e)}")
            raise
            
    def get_connection(self) -> redis.Redis:
        """获取Redis连接
        
        Returns:
            redis.Redis: Redis客户端实例
        """
        if not self._pool:
            self._create_pool()
        return redis.Redis(connection_pool=self._pool)
        
    def execute_with_retry(self, func, *args, max_retries=3, retry_delay=0.1, **kwargs):
        """执行Redis操作，支持重试
        
        Args:
            func: 要执行的函数
            max_retries: 最大重试次数
            retry_delay: 重试延迟(秒)
            
        Returns:
            Any: 函数执行结果
        """
        retries = 0
        last_error = None
        
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except (ConnectionError, RedisError) as e:
                last_error = e
                retries += 1
                if retries < max_retries:
                    logger.warning(f"Redis操作失败，正在重试({retries}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                    # 重新创建连接池
                    self._create_pool()
                    
        logger.error(f"Redis操作失败，重试{max_retries}次后放弃: {str(last_error)}")
        raise last_error
        
    def close(self):
        """关闭连接池"""
        if self._pool:
            self._pool.disconnect()
            logger.info("Redis连接池已关闭")
            
# 全局Redis管理器实例
redis_manager = RedisManager()

def redis_get(key: str) -> Optional[str]:
    """
    从Redis获取字符串值

    Args:
        key: Redis键

    Returns:
        Optional[str]: 存储的值，如果不存在则返回None
    """
    try:
        client = redis_manager.get_connection()
        value = client.get(key)
        return value
    except Exception as e:
        logger.error(f"Redis获取值失败 - 键:{key}, 错误:{str(e)}")
        return None

def redis_set(key: str, value: str, ex: int = None) -> bool:
    """
    设置Redis字符串值

    Args:
        key: Redis键
        value: 要存储的值
        ex: 过期时间(秒)，默认为None，表示不过期

    Returns:
        bool: 操作是否成功
    """
    try:
        client = redis_manager.get_connection()
        client.set(key, value, ex=ex)
        return True
    except Exception as e:
        logger.error(f"Redis设置值失败 - 键:{key}, 错误:{str(e)}")
        return False

def redis_delete(key: str) -> bool:
    """
    删除Redis键

    Args:
        key: Redis键

    Returns:
        bool: 操作是否成功
    """
    try:
        client = redis_manager.get_connection()
        client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Redis删除键失败 - 键:{key}, 错误:{str(e)}")
        return False

def redis_exists(key: str) -> bool:
    """
    检查Redis键是否存在

    Args:
        key: Redis键

    Returns:
        bool: 键是否存在
    """
    try:
        client = redis_manager.get_connection()
        return client.exists(key) > 0
    except Exception as e:
        logger.error(f"Redis检查键存在失败 - 键:{key}, 错误:{str(e)}")
        return False

def redis_get_json(key: str) -> Optional[Any]:
    """
    从Redis获取JSON值

    Args:
        key: Redis键

    Returns:
        Optional[Any]: 解析的JSON数据，如果不存在或出错返回None
    """
    try:
        value = redis_get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Redis获取JSON失败 - 键:{key}, 错误:{str(e)}")
        return None

def redis_set_json(key: str, value: Any, ex: int = None) -> bool:
    """
    将JSON数据存储到Redis

    Args:
        key: Redis键
        value: 要存储的数据，将被转换为JSON
        ex: 过期时间(秒)，默认为None，表示不过期

    Returns:
        bool: 操作是否成功
    """
    try:
        json_value = json.dumps(value)
        return redis_set(key, json_value, ex=ex)
    except Exception as e:
        logger.error(f"Redis设置JSON失败 - 键:{key}, 错误:{str(e)}")
        return False

def redis_incr(key: str, amount: int = 1) -> Optional[int]:
    """
    Redis计数器增加

    Args:
        key: Redis键
        amount: 增加量，默认为1

    Returns:
        Optional[int]: 增加后的值，如果出错返回None
    """
    try:
        client = redis_manager.get_connection()
        return client.incrby(key, amount)
    except Exception as e:
        logger.error(f"Redis增加计数失败 - 键:{key}, 增加量:{amount}, 错误:{str(e)}")
        return None

def redis_expire(key: str, seconds: int) -> bool:
    """
    设置Redis键过期时间

    Args:
        key: Redis键
        seconds: 过期秒数

    Returns:
        bool: 操作是否成功
    """
    try:
        client = redis_manager.get_connection()
        return client.expire(key, seconds)
    except Exception as e:
        logger.error(f"Redis设置过期时间失败 - 键:{key}, 秒数:{seconds}, 错误:{str(e)}")
        return False

def redis_ttl(key: str) -> Optional[int]:
    """
    获取Redis键剩余过期时间

    Args:
        key: Redis键

    Returns:
        Optional[int]: 剩余过期秒数，-1表示永不过期，-2表示不存在，None表示出错
    """
    try:
        client = redis_manager.get_connection()
        return client.ttl(key)
    except Exception as e:
        logger.error(f"Redis获取过期时间失败 - 键:{key}, 错误:{str(e)}")
        return None

# 为应用终止时注册清理函数
import atexit
atexit.register(redis_manager.close) 