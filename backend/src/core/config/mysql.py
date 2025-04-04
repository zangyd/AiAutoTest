from typing import Optional
from pydantic import BaseSettings

class MySQLSettings(BaseSettings):
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "autotest_user"
    MYSQL_PASSWORD: str = "123456"
    MYSQL_DATABASE: str = "autotest_platform"
    MYSQL_CHARSET: str = "utf8mb4"
    MYSQL_POOL_SIZE: int = 20
    MYSQL_POOL_RECYCLE: int = 3600
    
    class Config:
        env_prefix = "MYSQL_"
        case_sensitive = True

mysql_settings = MySQLSettings() 