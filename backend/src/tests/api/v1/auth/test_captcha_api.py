"""
验证码API测试模块
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from fastapi import status

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_captcha_manager():
    """创建模拟的验证码管理器"""
    mock = AsyncMock()
    mock.generate_captcha.return_value = {
        "captcha_id": "test_id",
        "captcha_image": "data:image/png;base64,iVBORw0KGgoA...",
        "expire_in": 300
    }
    mock.verify_captcha.return_value = True
    return mock


@pytest.fixture
def mock_app(app, mock_captcha_manager):
    """为测试准备模拟的应用"""
    # 模拟应用的依赖项
    app.dependency_overrides = {
        # 这里可以添加更多的依赖项覆盖
    }
    # 将模拟的验证码管理器添加到应用状态
    app.state.captcha_manager = mock_captcha_manager
    return app


class TestCaptchaAPI:
    """验证码API测试类"""
    
    async def test_generate_captcha(self, async_client, mock_app):
        """测试生成验证码API"""
        # 发送请求
        response = await async_client.post("/api/v1/auth/captcha")
        
        # 检查响应状态
        assert response.status_code == status.HTTP_200_OK
        
        # 检查响应内容
        data = response.json()
        assert "captcha_id" in data
        assert "captcha_image" in data
        assert "expire_in" in data
        assert data["captcha_id"] == "test_id"
        assert data["captcha_image"].startswith("data:image/png;base64,")
        assert data["expire_in"] == 300
    
    async def test_login_with_captcha_success(self, async_client, mock_app, mock_captcha_manager, mock_authenticate_user):
        """测试带验证码的成功登录"""
        # 设置验证码和认证状态
        mock_captcha_manager.verify_captcha.return_value = True
        
        # 登录数据
        login_data = {
            "username": "testuser",
            "password": "password123",
            "captcha_id": "test_id",
            "captcha_text": "1234"
        }
        
        # 发送请求
        response = await async_client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers={"User-Agent": "TestAgent"}
        )
        
        # 检查响应状态
        assert response.status_code == status.HTTP_200_OK
        
        # 检查响应内容包含访问令牌
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        
        # 验证验证码验证被调用
        mock_captcha_manager.verify_captcha.assert_called_once_with(
            "test_id", "1234"
        )
    
    async def test_login_with_captcha_failure(self, async_client, mock_app, mock_captcha_manager):
        """测试验证码验证失败的登录"""
        # 设置验证码验证失败
        mock_captcha_manager.verify_captcha.return_value = False
        
        # 登录数据
        login_data = {
            "username": "testuser",
            "password": "password123",
            "captcha_id": "test_id",
            "captcha_text": "wrong"
        }
        
        # 发送请求
        response = await async_client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers={"User-Agent": "TestAgent"}
        )
        
        # 检查响应状态 - 应为验证失败
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # 检查错误信息是否包含验证码相关内容
        data = response.json()
        assert "detail" in data
        assert "验证码" in data["detail"] or "captcha" in data["detail"].lower()
        
        # 验证验证码验证被调用
        mock_captcha_manager.verify_captcha.assert_called_once_with(
            "test_id", "wrong"
        )
    
    async def test_login_without_captcha(self, async_client, mock_app, mock_authenticate_user):
        """测试不提供验证码的登录"""
        # 登录数据 - 不包含验证码信息
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        
        # 发送请求
        response = await async_client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers={"User-Agent": "TestAgent"}
        )
        
        # 在设置了验证码要求的情况下，应该返回错误
        # 但如果系统配置为不强制验证码，则可能成功
        # 这里我们假设成功了，具体根据实际实现调整断言
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data 