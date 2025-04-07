"""
配置管理模块
"""
from .base_settings import BaseAppSettings
from pydantic import Field
from typing import Optional

class Settings(BaseAppSettings):
    """
    应用配置类
    """
    # SQLAlchemy配置
    SQLALCHEMY_ECHO: bool = Field(default=False)
    SQLALCHEMY_POOL_SIZE: int = Field(default=5)
    SQLALCHEMY_POOL_TIMEOUT: int = Field(default=10)
    SQLALCHEMY_POOL_RECYCLE: int = Field(default=3600)
    
    # JWT配置
    JWT_SECRET_KEY: str = Field(default="your-secret-key")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=10080)  # 7天
    
    # 安全配置
    MAX_LOGIN_ATTEMPTS: int = Field(default=5)
    LOGIN_ATTEMPT_TIMEOUT: int = Field(default=300)  # 5分钟
    PASSWORD_MIN_LENGTH: int = Field(default=8)
    PASSWORD_MAX_LENGTH: int = Field(default=32)
    
    # 日志配置
    LOG_FILE_MAX_BYTES: int = Field(default=10485760)  # 10MB
    LOG_FILE_BACKUP_COUNT: int = Field(default=5)
    
    # 认证安全配置
    ACCOUNT_LOCKOUT_MINUTES: int = Field(default=30)
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True)
    PASSWORD_REQUIRE_NUMBER: bool = Field(default=True)
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True)
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True)
    
    # 验证码配置
    CAPTCHA_ENABLED: bool = Field(default=True)
    CAPTCHA_LENGTH: int = Field(default=6)
    CAPTCHA_EXPIRE_MINUTES: int = Field(default=5)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._configure_for_environment()

    def _configure_for_environment(self) -> None:
        """根据环境配置特定的设置"""
        super()._configure_for_environment()
        
        if self.ENV == "test":
            # 测试环境特定配置
            self.ACCESS_TOKEN_EXPIRE_MINUTES = 5
            self.REFRESH_TOKEN_EXPIRE_MINUTES = 1
            self.ACCOUNT_LOCKOUT_MINUTES = 5
            self.CAPTCHA_ENABLED = False
        elif self.ENV == "production":
            # 生产环境特定配置
            self.CAPTCHA_ENABLED = True
            self.MAX_LOGIN_ATTEMPTS = 3
            self.ACCOUNT_LOCKOUT_MINUTES = 30
            self.PASSWORD_MIN_LENGTH = 12

settings = Settings() 