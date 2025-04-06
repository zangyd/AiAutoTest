"""
认证模块测试用例
"""
import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from backend.src.core.auth.schemas import TokenResponse, UserOut
from ..schemas import CaptchaResponse, LoginRequest, RefreshTokenRequest
from ..service import generate_captcha, verify_login, refresh_token

# 测试数据
TEST_USER = UserOut(
    id=1,
    username="test_user",
    email="test@example.com",
    is_active=True,
    is_superuser=False
)

TEST_TOKEN = TokenResponse(
    access_token="test_access_token",
    token_type="bearer",
    expires_in=3600,
    refresh_token="test_refresh_token"
)

@pytest.fixture
def mock_captcha_generator():
    with patch("....core.utils.captcha.CaptchaGenerator") as mock:
        instance = mock.return_value
        instance.generate.return_value = ("1234", "base64_image_data")
        yield instance

@pytest.fixture
def mock_captcha_cache():
    with patch("....core.cache.captcha.CaptchaCache") as mock:
        instance = mock.return_value
        instance.save_captcha.return_value = True
        instance.verify_captcha.return_value = True
        yield instance

@pytest.fixture
def mock_auth_service():
    with patch("....core.auth.service.auth_service") as mock:
        mock.authenticate_user.return_value = (TEST_USER, TEST_TOKEN)
        yield mock

class TestCaptcha:
    """验证码相关测试"""
    
    async def test_generate_captcha_success(self, mock_captcha_generator, mock_captcha_cache):
        """测试成功生成验证码"""
        response = await generate_captcha()
        assert isinstance(response, CaptchaResponse)
        assert response.image == "base64_image_data"
        assert len(response.captcha_id) > 0

    async def test_generate_captcha_failure(self, mock_captcha_generator, mock_captcha_cache):
        """测试生成验证码失败"""
        mock_captcha_cache.save_captcha.return_value = False
        with pytest.raises(HTTPException) as exc_info:
            await generate_captcha()
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "验证码生成失败"

class TestLogin:
    """登录相关测试"""

    async def test_login_success(self, mock_captcha_cache, mock_auth_service):
        """测试正常登录"""
        response = await verify_login(
            username="test_user",
            password="password",
            captcha_id="test_id",
            captcha_code="1234",
            remember=False
        )
        assert isinstance(response, TokenResponse)
        assert response == TEST_TOKEN

    async def test_login_invalid_captcha(self, mock_captcha_cache):
        """测试验证码错误"""
        mock_captcha_cache.verify_captcha.return_value = False
        with pytest.raises(HTTPException) as exc_info:
            await verify_login(
                username="test_user",
                password="password",
                captcha_id="test_id",
                captcha_code="wrong_code",
                remember=False
            )
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "验证码错误或已过期"

    async def test_login_invalid_credentials(self, mock_captcha_cache, mock_auth_service):
        """测试用户名或密码错误"""
        mock_auth_service.authenticate_user.side_effect = Exception("Invalid credentials")
        with pytest.raises(HTTPException) as exc_info:
            await verify_login(
                username="wrong_user",
                password="wrong_password",
                captcha_id="test_id",
                captcha_code="1234",
                remember=False
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "用户名或密码错误"

class TestTokenRefresh:
    """Token刷新相关测试"""

    async def test_refresh_token_success(self):
        """测试成功刷新token"""
        with patch("..service.refresh_access_token") as mock_refresh:
            mock_refresh.return_value = TEST_TOKEN
            response = await refresh_token("valid_refresh_token")
            assert isinstance(response, TokenResponse)
            assert response == TEST_TOKEN

    async def test_refresh_token_invalid(self):
        """测试无效的刷新token"""
        with patch("..service.refresh_access_token") as mock_refresh:
            mock_refresh.side_effect = Exception("Invalid refresh token")
            with pytest.raises(HTTPException) as exc_info:
                await refresh_token("invalid_refresh_token")
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "刷新令牌无效或已过期" 