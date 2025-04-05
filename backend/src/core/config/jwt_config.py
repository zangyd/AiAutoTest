from datetime import timedelta
from typing import Optional

from pydantic import BaseModel


class JWTSettings(BaseModel):
    """JWT配置设置"""
    # JWT密钥
    SECRET_KEY: str = "your-super-secret-key-please-change-in-production"
    # 算法
    ALGORITHM: str = "HS256"
    # 访问令牌过期时间（分钟）
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # 刷新令牌过期时间（天）
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # 令牌类型
    TOKEN_TYPE: str = "bearer"
    # 是否在响应中包含刷新令牌
    INCLUDE_REFRESH_TOKEN: bool = True
    # 令牌黑名单缓存过期时间（小时）
    TOKEN_BLACKLIST_EXPIRE_HOURS: int = 24

    @property
    def access_token_expires(self) -> timedelta:
        """获取访问令牌过期时间"""
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def refresh_token_expires(self) -> timedelta:
        """获取刷新令牌过期时间"""
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

    @property
    def blacklist_expires(self) -> timedelta:
        """获取黑名单缓存过期时间"""
        return timedelta(hours=self.TOKEN_BLACKLIST_EXPIRE_HOURS)


# 创建JWT设置实例
jwt_settings = JWTSettings() 