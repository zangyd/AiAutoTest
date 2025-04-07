"""认证API测试"""
import pytest
from unittest.mock import patch, AsyncMock

# 标记使用asyncio
pytestmark = pytest.mark.asyncio

class TestAuthAPI:
    """认证API测试类"""
    
    async def test_login_success(self, async_client):
        """测试登录成功"""
        # 准备请求数据
        login_data = {
            "username": "testuser",
            "password": "password"
        }
        
        # 发送登录请求
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        # 验证结果
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self, async_client):
        """测试登录失败 - 无效凭证"""
        # 准备请求数据
        login_data = {
            "username": "testuser",
            "password": "wrong_password"
        }
        
        # 发送登录请求
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        # 验证结果
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    async def test_logout(self, async_client, user_token):
        """测试登出"""
        # 使用模拟的TokenBlacklist
        with patch("api.v1.auth.router.token_blacklist") as mock_blacklist:
            # 设置mock返回值
            mock_blacklist.add_to_blacklist = AsyncMock(return_value=True)
            
            # 发送登出请求
            response = await async_client.post(
                "/api/v1/auth/logout",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            # 验证结果
            assert response.status_code == 200
            mock_blacklist.add_to_blacklist.assert_called_once()
            
            # 确认返回的消息
            data = response.json()
            assert "message" in data
            assert "success" in data["message"].lower()
    
    async def test_me(self, async_client, user_token, mock_user):
        """测试获取当前用户信息"""
        # 发送请求
        response = await async_client.get(
            "/api/v1/auth/me", 
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # 验证结果
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == mock_user.username
        assert data["email"] == mock_user.email
        
    async def test_invalid_token(self, async_client):
        """测试无效令牌"""
        # 使用无效令牌
        response = await async_client.get(
            "/api/v1/auth/me", 
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        # 验证结果
        assert response.status_code == 401 