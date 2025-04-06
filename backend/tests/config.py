from typing import Dict, Any
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# API测试配置
API_CONFIG = {
    "host": os.getenv("TEST_API_HOST", "localhost"),
    "port": int(os.getenv("TEST_API_PORT", "8000")),
    "protocol": os.getenv("TEST_API_PROTOCOL", "http"),
    "version": os.getenv("TEST_API_VERSION", "v1"),
    "timeout": int(os.getenv("TEST_API_TIMEOUT", "30")),
    "max_retries": int(os.getenv("TEST_API_MAX_RETRIES", "3"))
}

# 测试用户配置
TEST_USERS = {
    "admin": {
        "username": os.getenv("TEST_ADMIN_USERNAME", "admin"),
        "password": os.getenv("TEST_ADMIN_PASSWORD", "admin_password"),
        "email": "admin@example.com",
        "department": "技术部",
        "position": "管理员",
        "permissions": ["admin", "user_view", "user_manage"]
    },
    "user": {
        "username": os.getenv("TEST_USER_USERNAME", "test_user"),
        "password": os.getenv("TEST_USER_PASSWORD", "test_password"),
        "email": os.getenv("TEST_USER_EMAIL", "test@example.com"),
        "department": "技术部",
        "position": "工程师",
        "permissions": ["user_view"]
    }
}

# JWT配置
JWT_CONFIG = {
    "secret_key": os.getenv("TEST_JWT_SECRET", "test_secret_key"),
    "algorithm": os.getenv("TEST_JWT_ALGORITHM", "HS256"),
    "access_token_expire_minutes": int(os.getenv("TEST_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
    "refresh_token_expire_days": int(os.getenv("TEST_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
}

# 数据库测试配置
DB_CONFIG = {
    "host": os.getenv("TEST_DB_HOST", "localhost"),
    "port": int(os.getenv("TEST_DB_PORT", "5432")),
    "database": os.getenv("TEST_DB_NAME", "test_db"),
    "user": os.getenv("TEST_DB_USER", "test_user"),
    "password": os.getenv("TEST_DB_PASSWORD", "test_password")
}

# Redis测试配置
REDIS_CONFIG = {
    "host": os.getenv("TEST_REDIS_HOST", "localhost"),
    "port": int(os.getenv("TEST_REDIS_PORT", "6379")),
    "db": int(os.getenv("TEST_REDIS_DB", "1")),
    "password": os.getenv("TEST_REDIS_PASSWORD", "test_password")
}

# 测试环境配置
TEST_ENV = {
    "environment": os.getenv("TEST_ENVIRONMENT", "testing"),
    "skip_cleanup": os.getenv("TEST_SKIP_CLEANUP", "false").lower() == "true",
    "parallel_workers": int(os.getenv("TEST_PARALLEL_WORKERS", "4"))
} 