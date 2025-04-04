from typing import Optional
from pydantic import BaseSettings

class MongoDBSettings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "autotest_platform"
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 100
    MONGODB_TIMEOUT_MS: int = 5000
    
    class Config:
        env_prefix = "MONGODB_"
        case_sensitive = True

mongodb_settings = MongoDBSettings() 