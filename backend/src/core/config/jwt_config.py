"""JWT配置管理

管理JWT相关的配置项，包括密钥、算法、过期时间等
"""

import os
from datetime import timedelta
from functools import lru_cache
from pydantic import Field, field_validator
from typing import Optional
from .settings import Settings

class JWTSettings(Settings):
    """JWT配置类"""
    
    # JWT基础配置
    JWT_SECRET_KEY: str = Field(
        default="aabbccDFllx9823!!@@ddFFBBcde12345678",
        description="JWT密钥"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT算法"
    )
    JWT_TOKEN_TYPE: str = Field(
        default="Bearer",
        description="Token类型"
    )
    JWT_ISSUER: str = Field(
        default="autotest",
        description="Token发行者"
    )
    JWT_AUDIENCE: str = Field(
        default="autotest-users",
        description="Token接收者"
    )
    
    # Token过期时间配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="访问令牌过期时间(分钟)"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="刷新令牌过期时间(天)"
    )
    BLACKLIST_TOKEN_EXPIRES: int = Field(
        default=24 * 60,  # 24小时
        description="黑名单令牌过期时间(分钟)"
    )
    
    @field_validator("JWT_SECRET_KEY")
    def validate_jwt_secret_key(cls, v: str) -> str:
        """验证JWT密钥长度"""
        if len(v) < 32:
            raise ValueError("JWT密钥长度必须至少为32个字符")
        return v
    
    @field_validator("JWT_ALGORITHM")
    def validate_jwt_algorithm(cls, v: str) -> str:
        """验证JWT算法"""
        allowed_algorithms = ["HS256", "HS384", "HS512"]
        if v not in allowed_algorithms:
            raise ValueError(f"不支持的JWT算法: {v}. 支持的算法: {', '.join(allowed_algorithms)}")
        return v
    
    def get_access_token_expires(self) -> timedelta:
        """获取访问令牌过期时间"""
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    def get_refresh_token_expires(self) -> timedelta:
        """获取刷新令牌过期时间"""
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
    
    def get_blacklist_token_expires(self) -> timedelta:
        """获取黑名单令牌过期时间"""
        return timedelta(minutes=self.BLACKLIST_TOKEN_EXPIRES)
    
    def configure_for_environment(self) -> None:
        """根据环境配置特定的设置"""
        if self.ENV == "test":
            self.ACCESS_TOKEN_EXPIRE_MINUTES = 5
            self.REFRESH_TOKEN_EXPIRE_DAYS = 1
            self.BLACKLIST_TOKEN_EXPIRES = 300  # 5分钟
        elif self.ENV == "production":
            self.ACCESS_TOKEN_EXPIRE_MINUTES = 15
            self.REFRESH_TOKEN_EXPIRE_DAYS = 30
            self.BLACKLIST_TOKEN_EXPIRES = 7 * 24 * 60 * 60  # 7天

@lru_cache()
def get_jwt_settings() -> JWTSettings:
    """获取JWT配置实例"""
    try:
        settings = JWTSettings()
        settings.configure_for_environment()
        return settings
    except Exception as e:
        raise RuntimeError(f"加载JWT配置失败: {str(e)}")

# 创建JWT配置单例
jwt_settings = get_jwt_settings() 