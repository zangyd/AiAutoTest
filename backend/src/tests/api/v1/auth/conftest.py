"""认证API测试的Fixtures"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from fastapi import FastAPI

from core.config.settings import settings
from api.v1.auth.router import router as auth_router
from core.auth.schemas import UserOut, TokenData

# 为测试创建一个模拟的UserOut对象
@pytest.fixture
def mock_user():
    """创建一个测试用户"""
    return UserOut(
        id=1,
        username="testuser",
        email="test@example.com",
        phone="13800138000",
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        last_login=datetime.now()
    )

# 创建一个模拟的get_current_user函数
@pytest.fixture
def mock_get_current_user(mock_user):
    """创建一个模拟的get_current_user函数"""
    async def _get_current_user():
        return mock_user
    return _get_current_user

# 模拟AuthService.authenticate_user
@pytest.fixture
def mock_authenticate_user(mock_user):
    """创建一个模拟的authenticate_user方法"""
    async def _authenticate_user(username, password):
        if username == "testuser" and password == "password":
            return mock_user
        raise ValueError("Invalid credentials")
    return _authenticate_user

# 模拟core.auth.jwt.verify_token
@pytest.fixture
def mock_verify_token():
    """创建一个模拟的verify_token函数"""
    def _verify_token(token):
        return TokenData(sub="1", username="testuser")
    return _verify_token

# 创建测试应用
@pytest.fixture
def app(mock_authenticate_user, mock_verify_token, mock_get_current_user):
    """创建测试应用"""
    # 创建一个测试应用
    app = FastAPI()
    
    # 添加认证路由
    app.include_router(auth_router, prefix="/api/v1/auth")
    
    # 应用patchs
    with patch("core.auth.service.AuthService.authenticate_user", mock_authenticate_user), \
         patch("core.auth.jwt.verify_token", mock_verify_token), \
         patch("api.v1.auth.router.get_current_user", mock_get_current_user):
        
        yield app

# 创建测试客户端
@pytest.fixture
async def async_client(app):
    """创建一个异步测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# 创建一个模拟的有效token
@pytest.fixture
def user_token():
    """创建一个模拟的用户token"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJ0ZXN0dXNlciJ9.signature" 