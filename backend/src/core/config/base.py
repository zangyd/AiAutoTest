"""
基础配置模块
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, List

class BaseAppSettings(BaseSettings):
    """基础配置类"""
    
    # 环境配置
    ENV: str = Field(
        default="development",
        description="运行环境"
    )
    DEBUG: bool = Field(
        default=True,
        description="调试模式"
    )
    
    # 基础安全配置
    SECRET_KEY: str = Field(
        default="aabbccDFllx9823!!@@ddFFBBcde12345678",
        description="应用密钥"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"],
        description="允许的主机列表"
    )
    
    # 数据库配置
    MYSQL_HOST: str = Field(
        default="localhost",
        description="MySQL主机"
    )
    MYSQL_PORT: int = Field(
        default=3306,
        description="MySQL端口"
    )
    MYSQL_USER: str = Field(
        default="root",
        description="MySQL用户名"
    )
    MYSQL_PASSWORD: str = Field(
        default="Autotest@2024",
        description="MySQL密码"
    )
    MYSQL_DATABASE: str = Field(
        default="autotest",
        description="MySQL数据库名"
    )
    
    # Redis配置
    REDIS_HOST: str = Field(
        default="localhost",
        description="Redis主机"
    )
    REDIS_PORT: int = Field(
        default=6379,
        description="Redis端口"
    )
    REDIS_PASSWORD: Optional[str] = Field(
        default="Autotest@2024",
        description="Redis密码"
    )
    REDIS_DB: int = Field(
        default=0,
        description="Redis数据库索引"
    )
    
    # MongoDB配置
    MONGODB_HOST: str = Field(
        default="localhost",
        description="MongoDB主机"
    )
    MONGODB_PORT: int = Field(
        default=27017,
        description="MongoDB端口"
    )
    MONGODB_USER: str = Field(
        default="admin",
        description="MongoDB用户名"
    )
    MONGODB_PASSWORD: str = Field(
        default="Autotest@2024",
        description="MongoDB密码"
    )
    MONGODB_DATABASE: str = Field(
        default="admin",
        description="MongoDB数据库名"
    )
    MONGODB_AUTH_SOURCE: str = Field(
        default="admin",
        description="MongoDB认证源"
    )
    
    # 日志配置
    LOG_LEVEL: str = Field(
        default="INFO",
        description="日志级别"
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    LOG_DIR: str = Field(
        default="logs",
        description="日志目录"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_default=True,
        extra="allow"
    )
    
    def configure_for_environment(self) -> None:
        """根据环境配置特定的设置"""
        if self.ENV == "test":
            self.DEBUG = True
            self.MYSQL_DATABASE = "autotest_test"
            self.LOG_LEVEL = "DEBUG"
        elif self.ENV == "production":
            self.DEBUG = False
            self.LOG_LEVEL = "INFO" 