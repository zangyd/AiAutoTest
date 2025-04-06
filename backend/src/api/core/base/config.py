"""
基础配置管理
"""
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseSettings, Field, validator, ConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """系统配置"""
    # 基础配置
    PROJECT_NAME: str = "AutoTest Platform"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # 服务配置
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=4, env="WORKERS")
    
    # 安全配置
    SECRET_KEY: str = Field(default="your-super-secret-key", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    ALGORITHM: str = "HS256"
    
    # 跨域配置
    ALLOWED_HOSTS: List[str] = Field(default=["*"])
    CORS_ORIGINS: List[str] = Field(default=["*"])
    
    # 数据库配置
    DB_HOST: str = Field(default="localhost", env="DB_HOST")
    DB_PORT: int = Field(default=27017, env="DB_PORT")
    DB_NAME: str = Field(default="autotest", env="DB_NAME")
    DB_USER: Optional[str] = Field(default=None, env="DB_USER")
    DB_PASSWORD: Optional[str] = Field(default=None, env="DB_PASSWORD")
    
    # Redis配置
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # 文件上传配置
    UPLOAD_DIR: str = Field(default="uploads")
    MAX_UPLOAD_SIZE: int = Field(default=5 * 1024 * 1024)  # 5MB
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"]
    
    # 缓存配置
    CACHE_TTL: int = Field(default=60 * 60)  # 1小时
    
    # 邮件配置
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: Optional[int] = Field(default=None, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    @validator("UPLOAD_DIR")
    def validate_upload_dir(cls, v: str) -> str:
        """验证并创建上传目录"""
        os.makedirs(v, exist_ok=True)
        return v
    
    @property
    def mongodb_url(self) -> str:
        """获取MongoDB连接URL"""
        if self.DB_USER and self.DB_PASSWORD:
            return f"mongodb://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}"
        return f"mongodb://{self.DB_HOST}:{self.DB_PORT}"
    
    @property
    def redis_url(self) -> str:
        """获取Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )

@lru_cache()
def get_settings() -> Settings:
    """获取系统配置单例"""
    return Settings()

# 导出配置实例
settings = get_settings() 