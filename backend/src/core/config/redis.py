from typing import Optional
from pydantic import BaseSettings

class RedisSettings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = "Redis@2024"
    REDIS_POOL_SIZE: int = 20
    REDIS_TIMEOUT: int = 5
    REDIS_ENCODING: str = "utf-8"
    
    class Config:
        env_prefix = "REDIS_"
        case_sensitive = True

redis_settings = RedisSettings() 