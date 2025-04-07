"""
JWT令牌黑名单

管理已撤销的JWT令牌，使用Redis存储黑名单
"""
from typing import Optional, Dict, Any
import jwt
import time
from redis.asyncio import Redis
from datetime import timedelta

from core.config.settings import settings
from core.cache.cache_manager import CacheManager

class TokenBlacklist:
    """JWT令牌黑名单管理"""
    
    def __init__(self, redis: Redis):
        """
        初始化令牌黑名单
        
        Args:
            redis: Redis客户端
        """
        self.cache = CacheManager(
            redis=redis,
            key_prefix="jwt:blacklist:",
            default_expire=86400 * 7  # 默认7天过期
        )
    
    async def add_to_blacklist(self, token: str) -> bool:
        """
        将令牌添加到黑名单
        
        Args:
            token: JWT令牌
            
        Returns:
            bool: 是否成功添加
        """
        try:
            # 解码令牌以获取jti和过期时间
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_signature": True, "verify_exp": False}
            )
            
            # 使用令牌的jti或整个token作为键
            token_id = payload.get("jti", token)
            
            # 确定过期时间
            if "exp" in payload:
                # 计算剩余时间
                exp_timestamp = payload["exp"]
                current_timestamp = int(time.time())
                ttl = max(0, exp_timestamp - current_timestamp)
                
                # 添加额外时间作为安全边界
                ttl += 3600  # 额外1小时
            else:
                # 如果令牌没有exp字段，使用默认过期时间
                ttl = settings.JWT_BLACKLIST_TTL
            
            # 将令牌加入黑名单
            await self.cache.set(token_id, True, expire=ttl)
            return True
        except Exception:
            # 记录错误但不抛出异常
            return False
    
    async def is_blacklisted(self, token: str) -> bool:
        """
        检查令牌是否在黑名单中
        
        Args:
            token: JWT令牌或令牌ID
            
        Returns:
            bool: 是否在黑名单中
        """
        try:
            # 尝试解码令牌
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_signature": True, "verify_exp": False}
            )
            
            # 使用令牌的jti或整个token作为键
            token_id = payload.get("jti", token)
            
            # 检查是否在黑名单中
            return await self.cache.exists(token_id)
        except Exception:
            # 如果解码失败，尝试直接使用令牌作为键
            return await self.cache.exists(token)
    
    async def clear_expired(self) -> int:
        """
        清理过期的黑名单记录（Redis会自动清理，此方法主要用于测试）
        
        Returns:
            int: 清理的记录数量
        """
        # Redis会自动清理过期键，此方法仅用于测试
        return 0 