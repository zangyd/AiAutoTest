"""
内存缓存模块

提供基于内存的缓存实现，适用于单机部署场景
"""
import time
from typing import Any, Dict, Optional
from threading import Lock


class MemoryCache:
    """内存缓存管理类"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
    
    def get(self, key: str) -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            Any: 缓存值，不存在或已过期返回None
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            item = self._cache[key]
            if item["expire"] and item["expire"] < time.time():
                del self._cache[key]
                return None
            
            return item["value"]
    
    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间(秒)
            
        Returns:
            bool: 是否设置成功
        """
        with self._lock:
            self._cache[key] = {
                "value": value,
                "expire": time.time() + expire if expire else None
            }
            return True
    
    def delete(self, key: str) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否删除成功
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否存在且未过期
        """
        with self._lock:
            if key not in self._cache:
                return False
            
            item = self._cache[key]
            if item["expire"] and item["expire"] < time.time():
                del self._cache[key]
                return False
            
            return True
    
    def ttl(self, key: str) -> int:
        """
        获取键的剩余生存时间
        
        Args:
            key: 缓存键
            
        Returns:
            int: 剩余秒数，-1表示永不过期，-2表示不存在或已过期
        """
        with self._lock:
            if key not in self._cache:
                return -2
            
            item = self._cache[key]
            if not item["expire"]:
                return -1
            
            ttl = int(item["expire"] - time.time())
            if ttl <= 0:
                del self._cache[key]
                return -2
            
            return ttl
    
    def expire(self, key: str, seconds: int) -> bool:
        """
        设置键的过期时间
        
        Args:
            key: 缓存键
            seconds: 过期时间(秒)
            
        Returns:
            bool: 是否设置成功
        """
        with self._lock:
            if key not in self._cache:
                return False
            
            self._cache[key]["expire"] = time.time() + seconds
            return True
    
    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()


# 创建全局内存缓存实例
memory_cache = MemoryCache() 