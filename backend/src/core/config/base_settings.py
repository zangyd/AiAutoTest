"""
基础配置类

包含所有通用的配置项，其他配置类通过继承此类来复用通用配置
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field
from typing import Optional

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

class BaseAppSettings(BaseSettings):
    """基础配置类"""
    
    # 环境配置
    ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    
    # 数据库配置
    MYSQL_HOST: str = Field(default="localhost")
    MYSQL_PORT: int = Field(default=3306)
    MYSQL_USER: str = Field(default="root")
    MYSQL_PASSWORD: str = Field(default="")
    MYSQL_DATABASE: str = Field(default="autotest")
    
    # Redis配置
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: Optional[str] = Field(default=None)
    REDIS_DB: int = Field(default=0)
    
    # MongoDB配置
    MONGODB_HOST: str = Field(default="localhost")
    MONGODB_PORT: int = Field(default=27017)
    MONGODB_USER: str = Field(default="admin")
    MONGODB_PASSWORD: str = Field(default="")
    MONGODB_DATABASE: str = Field(default="admin")
    MONGODB_AUTH_SOURCE: str = Field(default="admin")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOG_DIR: str = Field(default="logs")
    
    # 安全配置
    SECRET_KEY: str = Field(default="your-secret-key")
    ALLOWED_HOSTS: list = Field(default=["*"])
    
    model_config = ConfigDict(
        env_file=[
            str(ROOT_DIR / ".env"),
            str(ROOT_DIR / ".env.test")
        ],
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_nested_delimiter="__",
        extra="allow"
    )
    
    def _configure_for_environment(self) -> None:
        """根据环境配置特定的设置"""
        if self.ENV == "test":
            self.MYSQL_DATABASE = "autotest_test"
            self.REDIS_DB = 1
            self.MONGODB_DATABASE = "autotest_test"
            self.DEBUG = True
        elif self.ENV == "production":
            self.DEBUG = False
            self.LOG_LEVEL = "INFO"
            self.ALLOWED_HOSTS = ["autotest.example.com"] 