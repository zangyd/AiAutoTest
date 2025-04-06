"""JWT配置管理

管理JWT相关的配置项，包括密钥、算法、过期时间等
"""

from datetime import timedelta
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class JWTSettings(BaseSettings):
    """JWT配置类"""
    
    model_config = ConfigDict(env_prefix="JWT_")
    
    # JWT密钥
    SECRET_KEY: str = "test_secret_key"
    
    # JWT算法
    ALGORITHM: str = "HS256"
    
    # 访问令牌过期时间（分钟）
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 刷新令牌过期时间（天）
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 令牌类型
    TOKEN_TYPE: str = "Bearer"
    
    @property
    def access_token_expires(self) -> timedelta:
        """访问令牌过期时间"""
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    @property
    def refresh_token_expires(self) -> timedelta:
        """刷新令牌过期时间"""
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
    
    @property
    def blacklist_token_expires(self) -> timedelta:
        """黑名单令牌过期时间
        
        使用较长的过期时间以确保令牌在被撤销后足够长的时间内保持在黑名单中
        """
        return max(
            self.access_token_expires,
            self.refresh_token_expires
        ) + timedelta(hours=1)  # 额外添加1小时作为安全边界

# 创建全局JWT配置实例
jwt_settings = JWTSettings() 