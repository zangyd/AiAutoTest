"""数据库配置模块"""
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """数据库配置类"""
    
    # 数据库URI
    DATABASE_URI: str = Field(
        default="sqlite:///./test.db",
        env="DATABASE_URI"
    )
    
    # 是否在应用启动时创建数据库表
    AUTO_CREATE_TABLES: bool = Field(
        default=True,
        env="AUTO_CREATE_TABLES"
    )
    
    # 数据库连接池大小
    POOL_SIZE: int = Field(
        default=5,
        env="DATABASE_POOL_SIZE"
    )
    
    # 是否回显SQL语句
    ECHO_SQL: bool = Field(
        default=False,
        env="DATABASE_ECHO_SQL"
    )
    
    # Redis数据库URI
    REDIS_URI: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URI"
    )
    
    # Redis连接池大小
    REDIS_POOL_SIZE: int = Field(
        default=10,
        env="REDIS_POOL_SIZE"
    )
    
    # Redis超时时间（秒）
    REDIS_TIMEOUT: int = Field(
        default=5,
        env="REDIS_TIMEOUT"
    ) 