"""
系统配置模块
"""
from functools import lru_cache
from typing import Optional, Dict, Any
from pydantic import Field, validator
from .base import BaseAppSettings

class Settings(BaseAppSettings):
    """系统配置类"""
    
    # 基本配置
    PROJECT_NAME: str = Field(default="AutoTest", description="项目名称")
    VERSION: str = Field(default="1.0.0", description="项目版本")
    API_V1_STR: str = Field(default="/api/v1", description="API前缀")
    
    # 数据库连接池配置
    AUTO_CREATE_TABLES: bool = Field(default=True, description="是否自动创建表")
    DATABASE_POOL_SIZE: int = Field(default=5, description="数据库连接池大小")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="连接池最大溢出数")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, description="连接回收时间(秒)")
    DATABASE_ECHO_SQL: bool = Field(default=False, description="是否打印SQL语句")
    
    # 安全配置
    MAX_LOGIN_ATTEMPTS: int = Field(default=5, description="最大登录尝试次数")
    ACCOUNT_LOCKOUT_MINUTES: int = Field(default=30, description="账户锁定时间(分钟)")
    PASSWORD_MIN_LENGTH: int = Field(default=8, description="密码最小长度")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True, description="密码是否需要特殊字符")
    PASSWORD_REQUIRE_NUMBER: bool = Field(default=True, description="密码是否需要数字")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True, description="密码是否需要大写字母")
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True, description="密码是否需要小写字母")
    
    # 验证码配置
    CAPTCHA_ENABLED: bool = Field(default=True, description="是否启用验证码")
    CAPTCHA_LENGTH: int = Field(default=6, description="验证码长度")
    CAPTCHA_EXPIRE_MINUTES: int = Field(default=5, description="验证码过期时间(分钟)")
    CAPTCHA_EXPIRE_SECONDS: int = Field(default=300, description="验证码过期时间(秒)")
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别"""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed_levels:
            raise ValueError(f"日志级别必须是以下之一: {', '.join(allowed_levels)}")
        return v.upper()
    
    @property
    def DATABASE_URL(self) -> str:
        """获取数据库URL"""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@"
            f"{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )
    
    @property
    def MONGODB_URL(self) -> str:
        """获取MongoDB URL"""
        return (
            f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@"
            f"{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DATABASE}"
            f"?authSource={self.MONGODB_AUTH_SOURCE}"
        )
    
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """重写dict方法，移除敏感信息"""
        d = super().dict(*args, **kwargs)
        # 移除敏感信息
        sensitive_keys = {
            "MYSQL_PASSWORD", "MONGODB_PASSWORD", "REDIS_PASSWORD",
            "JWT_SECRET_KEY"
        }
        return {k: "******" if k in sensitive_keys else v for k, v in d.items()}

@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()

# 创建配置单例
settings = get_settings() 