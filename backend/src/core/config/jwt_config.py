"""JWT配置管理

管理JWT相关的配置项，包括密钥、算法、过期时间等
"""

from datetime import timedelta
from .base_settings import BaseAppSettings
from pydantic import Field
from typing import Optional, ClassVar
from pydantic_settings import BaseSettings

class JWTSettings(BaseSettings):
    """JWT配置类"""
    
    # JWT密钥 - 用于签名令牌
    JWT_SECRET_KEY: str = Field(default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7", env="JWT_SECRET_KEY")
    
    # JWT算法
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    
    # 访问令牌过期时间（分钟）
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # 刷新令牌过期时间（天）
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # 黑名单过期时间（秒）- 默认7天
    JWT_BLACKLIST_TTL: int = Field(default=7 * 24 * 60 * 60, env="JWT_BLACKLIST_TTL")
    
    # 令牌类型
    JWT_TOKEN_TYPE: ClassVar[str] = "Bearer"
    
    class Config:
        """配置类"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
    
    @property
    def access_token_expires(self) -> timedelta:
        """访问令牌过期时间"""
        return timedelta(minutes=self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    @property
    def refresh_token_expires(self) -> timedelta:
        """刷新令牌过期时间"""
        return timedelta(days=self.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    @property
    def blacklist_token_expires(self) -> int:
        """
        获取黑名单令牌过期时间
        
        确保已撤销的令牌保留在黑名单中足够长的时间
        """
        # 使用的是较长的刷新令牌过期时间，加上1天的安全边界
        return self.JWT_BLACKLIST_TTL

    def _configure_for_environment(self) -> None:
        """根据环境配置特定的设置"""
        super()._configure_for_environment()
        
        if self.ENV == "test":
            self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 5
            self.JWT_REFRESH_TOKEN_EXPIRE_DAYS = 1
        elif self.ENV == "production":
            self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15
            self.JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30

# 创建全局JWT配置实例
jwt_settings = JWTSettings() 