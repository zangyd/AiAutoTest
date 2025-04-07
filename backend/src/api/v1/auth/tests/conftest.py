"""
认证模块测试配置
"""
import pytest
from typing import Dict, Generator, AsyncGenerator
import asyncio
import sys
from httpx import AsyncClient
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
import jwt

from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.testclient import TestClient

from core.database import get_db
from core.config.settings import settings
from core.auth.models import User
from api.services.user import UserService
from core.security import create_access_token, create_refresh_token, verify_token
from core.auth.service import AuthService
from api.v1.auth.router import router as auth_router, get_current_user
from core.auth.schemas import UserOut, TokenResponse

# 标记所有测试使用asyncio
pytestmark = pytest.mark.asyncio

# 模拟数据
mock_user_id = 1
mock_username = "testuser"
mock_email = "test@example.com"
mock_phone = "13800138000"
mock_now = datetime.utcnow()

# 创建令牌响应
def create_token_response(user_id, username):
    """创建令牌响应"""
    return {
        "access_token": "mock_access_token",
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": "mock_refresh_token"
    }

# 创建用户对象
def create_user_out() -> UserOut:
    """创建用户输出模型"""
    return UserOut(
        id=mock_user_id,
        username=mock_username,
        email=mock_email,
        phone=mock_phone,
        is_active=True,
        is_superuser=False,
        created_at=mock_now,
        updated_at=mock_now,
        last_login=mock_now
    )

# 模拟获取当前用户的函数
async def mock_get_current_user() -> User:
    """
    模拟获取当前用户
    
    Returns:
        User: 用户对象
    """
    user = MagicMock(spec=User)
    user.id = mock_user_id
    user.username = mock_username
    user.email = mock_email
    user.phone = mock_phone
    user.is_active = True
    user.is_superuser = False
    user.password_hash = "$2b$12$RQvE5l8TkKOK9fUP5ybT1.Bs9HezcKovgA1c0Jd7GgQEraHLW3UYK"  # 密码: "password"
    user.created_at = mock_now
    user.updated_at = mock_now
    user.last_login = mock_now
    return user

# 模拟AuthService类的方法
async def mock_authenticate_user(*args, **kwargs) -> User:
    """
    模拟用户认证
    
    Returns:
        User: 用户对象
    """
    return mock_get_current_user()

async def mock_create_access_token(self, user, remember=False):
    """模拟create_access_token方法"""
    return create_token_response(user.id, user.username)

async def mock_verify_token(*args, **kwargs) -> dict:
    """
    模拟验证JWT令牌
    
    Returns:
        dict: 解码后的令牌数据
    """
    return {
        "sub": "1",
        "username": mock_username,
        "email": mock_email,
        "is_active": True,
        "is_superuser": False
    }

# 创建测试应用程序
@pytest.fixture
def test_app():
    """测试应用程序"""
    # 创建FastAPI应用
    app = FastAPI()
    
    # 添加认证路由
    app.include_router(auth_router, prefix="/api/v1")
    
    # 依赖注入覆盖
    app.dependency_overrides = {}
    
    return app

@pytest.fixture
def db():
    """创建模拟数据库会话"""
    mock_db = MagicMock(spec=Session)
    return mock_db

@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = MagicMock(spec=User)
    user.id = mock_user_id
    user.username = mock_username 
    user.email = mock_email
    user.phone = mock_phone
    user.is_active = True
    user.is_superuser = False
    
    # 配置模拟查询
    db.query.return_value.filter.return_value.first.return_value = user
    
    return user

@pytest.fixture
def client(test_app):
    """同步测试客户端"""
    return TestClient(test_app)

@pytest.fixture
def mock_redis():
    """
    模拟Redis客户端
    
    Returns:
        AsyncMock: Redis客户端模拟对象
    """
    redis_mock = AsyncMock()
    
    # 模拟Redis方法
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = True
    redis_mock.exists.return_value = False
    
    return redis_mock

@pytest.fixture
def test_user():
    """
    测试用户
    
    Returns:
        User: 用户对象
    """
    return mock_get_current_user()

@pytest.fixture
def user_token():
    """
    用户令牌
    
    Returns:
        str: JWT令牌
    """
    payload = {
        "sub": str(mock_user_id),
        "username": mock_username,
        "email": mock_email,
        "is_active": True,
        "is_superuser": False,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

@pytest.fixture
def mock_authentication():
    """
    模拟认证
    """
    with patch("core.auth.service.AuthService.authenticate_user", side_effect=mock_authenticate_user):
        with patch("core.auth.jwt.verify_token", side_effect=mock_verify_token):
            yield

@pytest.fixture
async def override_get_redis():
    """覆盖get_redis依赖"""
    return await mock_redis()

@pytest.fixture
async def async_client(test_app, mock_authentication):
    """
    异步客户端
    
    Args:
        test_app: 测试应用程序
        mock_authentication: 模拟认证
        
    Returns:
        AsyncClient: 异步HTTP客户端
    """
    # 覆盖Redis依赖
    test_app.dependency_overrides["core.database.redis.get_redis"] = mock_redis
    
    # 创建和返回异步客户端
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client 