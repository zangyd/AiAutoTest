from src.api.base import StatusEnum
from src.api.v1.users import UserOut

# 测试用户配置
TEST_USER = UserOut(
    id=1,
    username="test_user",
    email="test@example.com",
    department="技术部",
    position="工程师",
    status=StatusEnum.ACTIVE
)

# 测试客户端配置
TEST_CLIENT_CONFIG = {
    "base_url": "http://test.example.com",
    "timeout": 30
}

# 测试环境配置
TEST_ENV_CONFIG = {
    "testing": True,
    "debug": True,
    "database_url": "sqlite:///./test.db"
} 