"""测试会话管理和令牌登出功能"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta

from core.config import settings
from .conftest import mock_authentication, create_user_out

class TestSessionManagement:
    """测试会话状态管理功能"""
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, async_client: AsyncClient, user_token: str):
        """测试刷新令牌功能"""
        # 使用模拟刷新令牌
        refresh_token = jwt.encode(
            {
                "sub": "1",
                "username": "testuser",
                "email": "test@example.com",
                "is_active": True,
                "is_superuser": False,
                "refresh": True,
                "exp": datetime.utcnow() + timedelta(days=7)
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        # 发送刷新令牌请求
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        # 断言
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["refresh_token"] == refresh_token  # 刷新令牌应该保持不变
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, async_client: AsyncClient):
        """测试无效的刷新令牌"""
        # 发送无效的刷新令牌请求
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        # 断言
        assert response.status_code == 401
        assert "detail" in response.json()
    
    @pytest.mark.asyncio
    async def test_refresh_token_expired(self, async_client: AsyncClient):
        """测试过期的刷新令牌"""
        # 创建过期的刷新令牌
        expired_token = jwt.encode(
            {
                "sub": "1",
                "username": "testuser",
                "email": "test@example.com",
                "is_active": True,
                "is_superuser": False,
                "refresh": True,
                "exp": datetime.utcnow() - timedelta(days=1)
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        # 发送过期的刷新令牌请求
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_token}
        )
        
        # 断言
        assert response.status_code == 401
        assert "detail" in response.json()
        assert response.json()["detail"] == "令牌已过期"


class TestLogoutManagement:
    """测试登出功能"""
    
    @pytest.mark.asyncio
    @patch("core.auth.token_blacklist.TokenBlacklist.add_to_blacklist")
    async def test_logout(self, mock_add_to_blacklist, async_client: AsyncClient, user_token: str):
        """测试登出功能"""
        # 模拟将令牌添加到黑名单
        mock_add_to_blacklist.return_value = True
        
        # 发送登出请求
        response = await async_client.post(
            "/api/v1/auth/logout",
            json={"token": user_token}
        )
        
        # 断言
        assert response.status_code == 204
        # 确认黑名单添加方法被调用
        mock_add_to_blacklist.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("core.auth.token_blacklist.TokenBlacklist.add_to_blacklist")
    async def test_logout_with_refresh_token(self, mock_add_to_blacklist, async_client: AsyncClient, user_token: str):
        """测试同时登出访问令牌和刷新令牌"""
        # 模拟将令牌添加到黑名单
        mock_add_to_blacklist.return_value = True
        
        # 创建刷新令牌
        refresh_token = jwt.encode(
            {
                "sub": "1",
                "username": "testuser",
                "email": "test@example.com",
                "refresh": True,
                "exp": datetime.utcnow() + timedelta(days=7)
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        # 发送登出请求
        response = await async_client.post(
            "/api/v1/auth/logout",
            json={
                "token": user_token,
                "refresh_token": refresh_token
            }
        )
        
        # 断言
        assert response.status_code == 204
        # 确认黑名单添加方法被调用两次（一次是访问令牌，一次是刷新令牌）
        assert mock_add_to_blacklist.call_count == 2
    
    @pytest.mark.asyncio
    @patch("core.auth.token_blacklist.TokenBlacklist.add_to_blacklist")
    async def test_logout_failure(self, mock_add_to_blacklist, async_client: AsyncClient, user_token: str):
        """测试登出失败的情况"""
        # 模拟将令牌添加到黑名单失败
        mock_add_to_blacklist.return_value = False
        
        # 发送登出请求
        response = await async_client.post(
            "/api/v1/auth/logout",
            json={"token": user_token}
        )
        
        # 断言
        assert response.status_code == 400
        assert response.json()["detail"] == "登出失败"
    
    @pytest.mark.asyncio
    @patch("core.auth.token_blacklist.TokenBlacklist.is_blacklisted")
    async def test_access_with_blacklisted_token(self, mock_is_blacklisted, async_client: AsyncClient, user_token: str):
        """测试使用已在黑名单中的令牌访问接口"""
        # 模拟令牌在黑名单中
        mock_is_blacklisted.return_value = True
        
        # 使用已在黑名单中的令牌访问受保护的接口
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # 断言
        assert response.status_code == 401
        assert response.json()["detail"] == "令牌已被撤销" 