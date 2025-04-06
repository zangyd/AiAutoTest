"""Pytest配置文件

配置测试环境和共享fixture
"""

import os
import pytest
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# MongoDB测试环境变量
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017/test_db")
os.environ.setdefault("MONGO_MAX_POOL_SIZE", "10")
os.environ.setdefault("MONGO_MIN_POOL_SIZE", "1")
os.environ.setdefault("MONGO_MAX_IDLE_TIME", "1000")
os.environ.setdefault("MONGO_CONNECT_TIMEOUT", "1000")
os.environ.setdefault("MONGO_SERVER_SELECTION_TIMEOUT", "1000")

# MySQL测试环境变量
os.environ.setdefault("MYSQL_URL", "mysql+pymysql://test:test@localhost:3306/test_db")
os.environ.setdefault("MYSQL_POOL_SIZE", "5")
os.environ.setdefault("MYSQL_MAX_OVERFLOW", "10")
os.environ.setdefault("MYSQL_POOL_TIMEOUT", "30")
os.environ.setdefault("MYSQL_POOL_RECYCLE", "3600")
os.environ.setdefault("MYSQL_ECHO", "True")

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 创建测试目录
    os.makedirs("/tmp/db_backup_test", exist_ok=True)
    
    yield
    
    # 清理测试目录
    if os.path.exists("/tmp/db_backup_test"):
        for root, dirs, files in os.walk("/tmp/db_backup_test", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir("/tmp/db_backup_test") 