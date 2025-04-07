"""
系统核心配置模块
"""
from core.config.base_settings import BaseAppSettings
from pydantic import Field
from typing import List, Optional

class Settings(BaseAppSettings):
    """系统核心配置类"""
    
    # 系统配置
    SYSTEM_NAME: str = Field(default="AutoTest System")
    SYSTEM_VERSION: str = Field(default="1.0.0")
    
    # 服务配置
    SERVICE_HOST: str = Field(default="0.0.0.0")
    SERVICE_PORT: int = Field(default=8000)
    SERVICE_WORKERS: int = Field(default=4)
    
    # 安全配置
    CORS_ORIGINS: List[str] = Field(default=["*"])
    CORS_METHODS: List[str] = Field(default=["*"])
    CORS_HEADERS: List[str] = Field(default=["*"])
    
    # 文件系统配置
    UPLOAD_DIR: str = Field(default="uploads")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    ALLOWED_EXTENSIONS: List[str] = Field(default=[".jpg", ".png", ".pdf", ".xlsx"])
    
    # 缓存配置
    CACHE_TYPE: str = Field(default="redis")
    CACHE_PREFIX: str = Field(default="autotest:")
    CACHE_DEFAULT_TIMEOUT: int = Field(default=300)
    
    # 会话配置
    SESSION_TYPE: str = Field(default="redis")
    SESSION_PERMANENT: bool = Field(default=True)
    SESSION_USE_SIGNER: bool = Field(default=True)
    SESSION_KEY_PREFIX: str = Field(default="session:")
    
    def _configure_for_environment(self) -> None:
        """根据环境配置特定的设置"""
        super()._configure_for_environment()
        
        if self.ENV == "test":
            self.SERVICE_PORT = 8001
            self.SERVICE_WORKERS = 1
            self.CACHE_DEFAULT_TIMEOUT = 60
        elif self.ENV == "production":
            self.CORS_ORIGINS = ["https://autotest.example.com"]
            self.SERVICE_WORKERS = 8
            self.MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

# 创建全局系统配置实例
system_settings = Settings() 