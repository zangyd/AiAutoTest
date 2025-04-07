"""
认证API测试模块
"""
import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.orm import Session

from core.auth.models import User

pytestmark = pytest.mark.asyncio

class TestAuthAPI:
    """认证API测试类"""
    
    async def test_login_success(self, async_client: AsyncClient, db: Session, test_user: User):
        """测试登录成功"""
        response = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.username,
                "password": "Test@123"  # 测试用户的密码
            }
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """测试登录失败-无效凭证"""
        response = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent",
                "password": "wrongpassword"
            }
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_login_json(self, async_client: AsyncClient, db: Session, test_user: User):
        """测试JSON登录成功"""
        response = await async_client.post(
            "/api/v1/auth/login-json",
            json={
                "username": test_user.username,
                "password": "Test@123",
                "remember": True
            }
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_refresh_token(self, async_client: AsyncClient, user_token: dict):
        """测试刷新令牌"""
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": user_token["refresh_token"]
            }
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_refresh_token_invalid(self, async_client: AsyncClient):
        """测试刷新令牌失败-无效令牌"""
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": "invalid_token"
            }
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_get_current_user(self, async_client: AsyncClient, user_token: dict):
        """测试获取当前用户信息"""
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user_token['access_token']}"}
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "is_active" in data
    
    async def test_logout(self, async_client: AsyncClient, user_token: dict):
        """测试登出"""
        response = await async_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {user_token['access_token']}"}
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "登出成功"
