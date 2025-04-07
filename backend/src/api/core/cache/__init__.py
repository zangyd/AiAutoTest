"""
缓存模块

重导出核心缓存功能
"""
from ....core.cache.cache_manager import CacheManager
from ....core.cache.memory import MemoryCache, memory_cache
from ....core.cache.captcha import CaptchaCache

__all__ = [
    'CacheManager',
    'MemoryCache',
    'memory_cache',
    'CaptchaCache',
] 