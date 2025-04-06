"""缓存管理模块

提供Redis缓存管理功能，包括：
- 缓存键管理
- 过期时间管理
- 批量操作
- 分布式锁
- 缓存装饰器
"""

from .cache_manager import CacheManager

__all__ = ["CacheManager"] 