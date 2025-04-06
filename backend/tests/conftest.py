import pytest
from fastapi.testclient import TestClient
from main import app
from tests.config import TEST_USERS
from core.auth.jwt import jwt_handler

@pytest.fixture
def client() -> TestClient:
    """创建测试客户端"""
    return TestClient(app)

@pytest.fixture
def test_user():
    """测试用户数据"""
    return TEST_USERS["user"]

@pytest.fixture
def admin_user():
    """管理员用户数据"""
    return TEST_USERS["admin"]

@pytest.fixture
def admin_token():
    """管理员令牌"""
    return jwt_handler.create_token({"sub": TEST_USERS["admin"]["username"]})

@pytest.fixture
def user_token():
    """普通用户令牌"""
    return jwt_handler.create_token({"sub": TEST_USERS["user"]["username"]})

@pytest.fixture
def admin_headers(admin_token):
    """管理员请求头"""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def user_headers(user_token):
    """普通用户请求头"""
    return {"Authorization": f"Bearer {user_token}"} 