"""Redis缓存管理器

提供统一的缓存操作接口，支持：
- 键前缀管理
- 过期时间管理
- 批量操作
- 缓存策略
- 原子操作
- 分布式锁
"""

from typing import Optional, Any, List, Dict, Union
from datetime import timedelta
import json
import asyncio
from redis.asyncio import Redis
from redis.exceptions import LockError, ConnectionError
from core.cache.redis_manager import (
    redis_get,
    redis_set,
    redis_delete,
    redis_exists,
    redis_get_json,
    redis_set_json,
    redis_incr,
    redis_expire,
    redis_ttl
)
import logging
import threading
from redis import Redis
from redis.exceptions import RedisError
from .redis_manager import redis_manager

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis缓存管理器"""
    
    def __init__(
        self,
        redis_client: Redis,
        key_prefix: str = "",
        default_expire: int = 300,
        json_encoder = None,
        json_decoder = None
    ):
        """初始化缓存管理器
        
        Args:
            redis_client: Redis客户端实例
            key_prefix: 键前缀
            default_expire: 默认过期时间(秒)
            json_encoder: JSON编码器
            json_decoder: JSON解码器
        """
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.default_expire = default_expire
        self.json_encoder = json_encoder
        self.json_decoder = json_decoder
        self.lock = threading.Lock()
        
    def _build_key(self, key: str) -> str:
        """构建缓存键
        
        Args:
            key: 原始键名
            
        Returns:
            str: 添加前缀后的键名
        """
        return f"{self.key_prefix}:{key}" if self.key_prefix else key
        
    def _serialize(self, value: Any) -> str:
        """序列化值
        
        Args:
            value: 要序列化的值
            
        Returns:
            str: 序列化后的字符串
        """
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float, bool)):
            return str(value)
        return json.dumps(value, cls=self.json_encoder)
        
    def _deserialize(self, value: Optional[Union[bytes, str]]) -> Any:
        """反序列化值
        
        Args:
            value: 要反序列化的字节串或字符串
            
        Returns:
            Any: 反序列化后的值
        """
        if value is None:
            return None
            
        # 如果已经是字符串，直接返回
        if isinstance(value, str):
            return value
            
        # 如果是字节，尝试解码
        if isinstance(value, bytes):
            try:
                return value.decode('utf-8')
            except UnicodeDecodeError:
                return value
                
        # 其他类型，尝试转换为字符串
        return str(value)
        
    def get_sync(self, key: str, default: Any = None) -> Any:
        """同步获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            Any: 缓存值或默认值
        """
        with self.lock:
            try:
                full_key = self._build_key(key)
                logger.info(f"正在获取缓存 - 原始键:{key}, 完整键:{full_key}")
                
                # 检查键是否存在
                exists = self.redis.exists(full_key)
                logger.info(f"键是否存在: {exists}")
                
                # 获取TTL
                ttl = self.redis.ttl(full_key)
                logger.info(f"键的TTL: {ttl}秒")
                
                value = redis_manager.execute_with_retry(
                    self.redis.get,
                    full_key
                )
                
                if value is None:
                    logger.warning(f"缓存未命中 - 键:{full_key}")
                    return default
                    
                deserialized = self._deserialize(value)
                logger.info(f"缓存命中 - 键:{full_key}, 原始值类型:{type(value)}, 反序列化后类型:{type(deserialized)}")
                return deserialized
                
            except RedisError as e:
                logger.error(f"获取缓存失败 - 键:{key}, 错误:{str(e)}", exc_info=True)
                return default
                
    def set_sync(
        self,
        key: str,
        value: Any,
        expire_seconds: Optional[int] = None
    ) -> bool:
        """同步设置缓存值
        
        Args:
            key: 缓存键
            value: 要缓存的值
            expire_seconds: 过期时间(秒)
            
        Returns:
            bool: 操作是否成功
        """
        with self.lock:
            try:
                full_key = self._build_key(key)
                serialized = self._serialize(value)
                expire = expire_seconds if expire_seconds is not None else self.default_expire
                
                logger.info(f"正在设置缓存 - 键:{full_key}, 值:{value}, 序列化后:{serialized}, 过期时间:{expire}秒")
                
                def set_with_expire():
                    with self.redis.pipeline() as pipe:
                        pipe.setex(
                            full_key,
                            expire,
                            serialized
                        )
                        result = pipe.execute()
                        logger.info(f"缓存设置结果: {result}")
                        return True
                    
                success = redis_manager.execute_with_retry(set_with_expire)
                if success:
                    logger.info(f"缓存设置成功 - 键:{full_key}")
                else:
                    logger.error(f"缓存设置失败 - 键:{full_key}")
                return success
                
            except RedisError as e:
                logger.error(f"设置缓存失败 - 键:{key}, 错误:{str(e)}", exc_info=True)
                return False
                
    def delete_sync(self, key: str) -> bool:
        """同步删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 操作是否成功
        """
        with self.lock:
            try:
                full_key = self._build_key(key)
                return bool(redis_manager.execute_with_retry(
                    self.redis.delete,
                    full_key
                ))
            except RedisError as e:
                logger.error(f"删除缓存失败 - 键:{key}, 错误:{str(e)}")
                return False
                
    def exists_sync(self, key: str) -> bool:
        """同步检查缓存是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否存在
        """
        with self.lock:
            try:
                full_key = self._build_key(key)
                return bool(redis_manager.execute_with_retry(
                    self.redis.exists,
                    full_key
                ))
            except RedisError as e:
                logger.error(f"检查缓存是否存在失败 - 键:{key}, 错误:{str(e)}")
                return False
                
    def expire_sync(self, key: str, seconds: int) -> bool:
        """同步设置过期时间
        
        Args:
            key: 缓存键
            seconds: 过期时间(秒)
            
        Returns:
            bool: 操作是否成功
        """
        with self.lock:
            try:
                full_key = self._build_key(key)
                return bool(redis_manager.execute_with_retry(
                    self.redis.expire,
                    full_key,
                    seconds
                ))
            except RedisError as e:
                logger.error(f"设置过期时间失败 - 键:{key}, 错误:{str(e)}")
                return False
            
    async def get(self, key: str, default: Any = None) -> Any:
        """异步获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            Any: 缓存值或默认值
        """
        try:
            value = await self.redis.get(self._build_key(key))
            if value is None:
                return default
            return json.loads(value, cls=self.json_decoder)
        except (json.JSONDecodeError, ConnectionError):
            return default
            
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """异步设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间(秒或timedelta)
            nx: 键不存在时才设置
            xx: 键存在时才设置
            
        Returns:
            bool: 是否设置成功
        """
        key = self._build_key(key)
        try:
            value = json.dumps(value, cls=self.json_encoder)
            if expire is None:
                expire = self.default_expire
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
                
            return await self.redis.set(
                key,
                value,
                ex=expire,
                nx=nx,
                xx=xx
            )
        except (TypeError, ConnectionError):
            return False
            
    async def delete(self, key: str) -> bool:
        """异步删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否删除成功
        """
        try:
            return bool(await self.redis.delete(self._build_key(key)))
        except ConnectionError:
            return False
            
    async def exists(self, key: str) -> bool:
        """异步检查缓存是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否存在
        """
        try:
            return bool(await self.redis.exists(self._build_key(key)))
        except ConnectionError:
            return False
            
    async def expire(
        self,
        key: str,
        expire: Union[int, timedelta]
    ) -> bool:
        """异步设置过期时间
        
        Args:
            key: 缓存键
            expire: 过期时间(秒或timedelta)
            
        Returns:
            bool: 是否设置成功
        """
        try:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            return await self.redis.expire(self._build_key(key), expire)
        except ConnectionError:
            return False
            
    async def ttl(self, key: str) -> int:
        """异步获取剩余过期时间
        
        Args:
            key: 缓存键
            
        Returns:
            int: 剩余秒数，-1表示永不过期，-2表示不存在
        """
        try:
            return await self.redis.ttl(self._build_key(key))
        except ConnectionError:
            return -2
            
    async def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """异步增加计数器值
        
        Args:
            key: 缓存键
            amount: 增加量
            
        Returns:
            Optional[int]: 增加后的值，失败返回None
        """
        try:
            return await self.redis.incrby(self._build_key(key), amount)
        except ConnectionError:
            return None
            
    async def decr(self, key: str, amount: int = 1) -> Optional[int]:
        """异步减少计数器值
        
        Args:
            key: 缓存键
            amount: 减少量
            
        Returns:
            Optional[int]: 减少后的值，失败返回None
        """
        try:
            return await self.redis.decrby(self._build_key(key), amount)
        except ConnectionError:
            return None
            
    async def mget(self, keys: List[str], default: Any = None) -> List[Any]:
        """批量获取缓存值
        
        Args:
            keys: 缓存键列表
            default: 默认值
            
        Returns:
            List[Any]: 缓存值列表
        """
        try:
            values = await self.redis.mget([self._build_key(key) for key in keys])
            return [
                json.loads(value, cls=self.json_decoder) if value is not None else default
                for value in values
            ]
        except (json.JSONDecodeError, ConnectionError):
            return [default] * len(keys)
            
    async def mset(
        self,
        mapping: Dict[str, Any],
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """批量设置缓存值
        
        Args:
            mapping: 键值映射
            expire: 过期时间(秒或timedelta)
            
        Returns:
            bool: 是否全部设置成功
        """
        try:
            # 构建新的映射
            new_mapping = {
                self._build_key(key): json.dumps(value, cls=self.json_encoder)
                for key, value in mapping.items()
            }
            
            # 使用管道执行批量操作
            async with self.redis.pipeline() as pipe:
                # 设置所有值
                await pipe.mset(new_mapping)
                
                # 如果指定了过期时间，为每个键设置过期时间
                if expire is not None:
                    if isinstance(expire, timedelta):
                        expire = int(expire.total_seconds())
                    for key in new_mapping.keys():
                        await pipe.expire(key, expire)
                
                # 执行管道操作
                results = await pipe.execute()
                
                # 验证所有操作是否成功
                return all(results)
                
        except (TypeError, ConnectionError):
            return False
            
    async def delete_many(self, keys: List[str]) -> int:
        """批量删除缓存
        
        Args:
            keys: 缓存键列表
            
        Returns:
            int: 成功删除的数量
        """
        try:
            return await self.redis.delete(*[self._build_key(key) for key in keys])
        except ConnectionError:
            return 0
            
    async def clear_prefix(self, prefix: str = "") -> int:
        """清除指定前缀的缓存
        
        Args:
            prefix: 键前缀(为空则使用默认前缀)
            
        Returns:
            int: 删除的键数量
        """
        try:
            prefix = self._build_key(prefix)
            keys = []
            async for key in self.redis.scan_iter(f"{prefix}*"):
                keys.append(key)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except ConnectionError:
            return 0
            
    async def acquire_lock(
        self,
        key: str,
        expire: int = 10,
        timeout: int = None,
        retry_delay: float = 0.2,
        retry_count: int = None
    ) -> bool:
        """获取分布式锁
        
        Args:
            key: 锁键名
            expire: 锁过期时间(秒)
            timeout: 获取锁超时时间(秒)
            retry_delay: 重试延迟(秒)
            retry_count: 重试次数
            
        Returns:
            bool: 是否获取成功
        """
        key = f"lock:{self._build_key(key)}"
        retry = 0
        start = asyncio.get_event_loop().time()
        
        while True:
            try:
                if await self.redis.set(key, 1, ex=expire, nx=True):
                    return True
                    
                retry += 1
                if retry_count is not None and retry >= retry_count:
                    return False
                    
                if timeout is not None:
                    if asyncio.get_event_loop().time() - start >= timeout:
                        return False
                        
                await asyncio.sleep(retry_delay)
            except ConnectionError:
                return False
                
    async def release_lock(self, key: str) -> bool:
        """释放分布式锁
        
        Args:
            key: 锁键名
            
        Returns:
            bool: 是否释放成功
        """
        try:
            key = f"lock:{self._build_key(key)}"
            return bool(await self.redis.delete(key))
        except ConnectionError:
            return False
            
    def cache_decorator(
        self,
        key_pattern: str,
        expire: Optional[Union[int, timedelta]] = None,
        key_builder: Optional[callable] = None
    ):
        """缓存装饰器
        
        Args:
            key_pattern: 缓存键模式，支持格式化字符串
            expire: 过期时间(秒或timedelta)
            key_builder: 自定义缓存键生成函数
            
        Returns:
            callable: 装饰器函数
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # 生成缓存键
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    cache_key = key_pattern.format(*args, **kwargs)
                    
                # 尝试从缓存获取
                cached = await self.get(cache_key)
                if cached is not None:
                    return cached
                    
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 缓存结果
                await self.set(cache_key, result, expire=expire)
                
                return result
                
            return wrapper
            
        return decorator 