"""
认证API测试
"""
import pytest
from unittest.mock import patch, AsyncMock
import json
from httpx import AsyncClient
from fastapi import status

pytestmark = pytest.mark.asyncio


class TestAuthAPI:
    """认证API测试类"""

    # 测试登录成功
    async def test_login_success(self, async_client):
        """测试用户登录成功"""
        # 准备登录数据
        form_data = {
            "username": "testuser",
            "password": "password"
        }

        # 模拟create_tokens返回值
        with patch("core.auth.service.AuthService.create_tokens", 
                   return_value=("access_token", "refresh_token")):
            # 发送登录请求
            response = await async_client.post(
                "/api/v1/auth/login",
                data=form_data
            )

        # 断言响应
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["access_token"] == "access_token"
        assert data["refresh_token"] == "refresh_token"
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] == 1800  # 30分钟

    # 测试登录失败
    async def test_login_invalid_credentials(self, async_client):
        """测试用户登录失败 - 无效凭据"""
        # 准备登录数据
        form_data = {
            "username": "invalid",
            "password": "invalid"
        }

        # 模拟认证失败
        with patch("core.auth.service.AuthService.authenticate_user", 
                   side_effect=Exception("Invalid credentials")):
            # 发送登录请求
            response = await async_client.post(
                "/api/v1/auth/login",
                data=form_data
            )

        # 断言响应
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # 测试刷新令牌
    async def test_refresh_token(self, async_client):
        """测试刷新令牌"""
        # 准备请求数据
        refresh_data = {
            "refresh_token": "old_refresh_token"
        }

        # 模拟refresh_access_token返回值
        with patch("core.auth.service.AuthService.refresh_access_token", 
                   return_value="new_access_token"):
            # 发送刷新请求
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json=refresh_data
            )

        # 断言响应
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["access_token"] == "new_access_token"
        assert data["refresh_token"] == "old_refresh_token"  # refresh_token不变
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] == 1800  # 30分钟

    # 测试刷新令牌失败
    async def test_refresh_token_invalid(self, async_client):
        """测试刷新令牌失败 - 无效令牌"""
        # 准备请求数据
        refresh_data = {
            "refresh_token": "invalid_refresh_token"
        }

        # 模拟refresh_access_token失败
        with patch("core.auth.service.AuthService.refresh_access_token", 
                   side_effect=Exception("Invalid refresh token")):
            # 发送刷新请求
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json=refresh_data
            )

        # 断言响应
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # 测试登出
    async def test_logout(self, async_client):
        """测试用户登出"""
        # 准备请求数据
        logout_data = {
            "token": "access_token",
            "refresh_token": "refresh_token"
        }

        # 模拟logout返回值
        with patch("core.auth.service.AuthService.logout", return_value=True):
            # 发送登出请求
            response = await async_client.post(
                "/api/v1/auth/logout",
                json=logout_data
            )

        # 断言响应
        assert response.status_code == status.HTTP_204_NO_CONTENT

    # 测试登出失败
    async def test_logout_failed(self, async_client):
        """测试用户登出失败"""
        # 准备请求数据
        logout_data = {
            "token": "invalid_token",
            "refresh_token": "invalid_refresh_token"
        }

        # 模拟logout失败
        with patch("core.auth.service.AuthService.logout", return_value=False):
            # 发送登出请求
            response = await async_client.post(
                "/api/v1/auth/logout",
                json=logout_data
            )

        # 断言响应
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # 测试获取当前用户信息
    async def test_get_current_user(self, async_client, user_token, mock_user):
        """测试获取当前用户信息"""
        # 设置请求头
        headers = {
            "Authorization": f"Bearer {user_token}"
        }

        # 发送请求
        response = await async_client.get(
            "/api/v1/auth/me",
            headers=headers
        )

        # 断言响应
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == mock_user.id
        assert data["username"] == mock_user.username
        assert data["email"] == mock_user.email
        assert data["is_active"] == mock_user.is_active

    # 测试无效token
    async def test_invalid_token(self, async_client):
        """测试无效的认证token"""
        # 设置请求头
        headers = {
            "Authorization": "Bearer invalid_token"
        }

        # 模拟get_current_user失败
        with patch("api.v1.auth.router.get_current_user", 
                   side_effect=Exception("Invalid token")):
            # 发送请求
            response = await async_client.get(
                "/api/v1/auth/me",
                headers=headers
            )

        # 断言响应
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR 