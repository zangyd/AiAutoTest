"""
数据库配置模块
"""
from pydantic_settings import BaseSettings
from typing import Optional

class MySQLSettings(BaseSettings):
    """MySQL配置"""
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    @property
    def DATABASE_URL(self) -> str:
        """获取数据库URL"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    class Config:
        env_file = ".env"

class MongoDBSettings(BaseSettings):
    """MongoDB配置"""
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_DATABASE: str

    @property
    def DATABASE_URL(self) -> str:
        """获取数据库URL"""
        return f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DATABASE}"

    class Config:
        env_file = ".env"

class RedisSettings(BaseSettings):
    """Redis配置"""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    @property
    def REDIS_URL(self) -> str:
        """获取Redis URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"

# 创建配置实例
mysql_settings = MySQLSettings()
mongodb_settings = MongoDBSettings()
redis_settings = RedisSettings() 