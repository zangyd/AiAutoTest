"""
配置模块

管理应用程序的所有配置项
"""
from typing import Optional
from core.config.base_settings import BaseAppSettings
from pydantic import Field

class Settings(BaseAppSettings):
    """应用程序配置"""
    
    # 应用配置
    APP_NAME: str = Field(default="AutoTest API")
    APP_VERSION: str = Field(default="1.0.0")
    
    # API配置
    API_PREFIX: str = Field(default="/api")
    API_V1_PREFIX: str = Field(default="/v1")
    
    # 文件上传配置
    UPLOAD_DIR: str = Field(default="uploads")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    
    @property
    def database_url(self) -> str:
        """获取数据库URL"""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@"
            f"{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )
    
    @property
    def redis_url(self) -> str:
        """获取Redis URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def mongo_url(self) -> str:
        """获取MongoDB URL"""
        auth = (
            f"{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@"
            if self.MONGODB_USER and self.MONGODB_PASSWORD
            else ""
        )
        return f"mongodb://{auth}{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DATABASE}"

    def _configure_for_environment(self) -> None:
        """根据环境配置特定的设置"""
        super()._configure_for_environment()
        
        if self.ENV == "test":
            self.APP_NAME = "AutoTest API (Test)"
        elif self.ENV == "production":
            self.APP_NAME = "AutoTest API (Production)"

# 创建全局配置实例
settings = Settings() 