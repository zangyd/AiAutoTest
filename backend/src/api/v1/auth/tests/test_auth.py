"""
认证模块测试用例
"""
import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock, call
from backend.src.core.auth.schemas import TokenResponse, UserOut
from backend.src.api.v1.auth.schemas import CaptchaResponse, LoginRequest, RefreshTokenRequest
from backend.src.api.v1.auth.service import generate_captcha, verify_login, refresh_token
from backend.src.api.v1.auth.constants import AuthErrorCode

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

TEST_CAPTCHA_TEXT = "1234"
TEST_CAPTCHA_IMAGE = "data:image/png;base64,test_image_data"

@pytest.fixture
def mock_captcha_generator():
    with patch("backend.src.core.utils.captcha.CaptchaGenerator") as mock:
        instance = mock.return_value
        instance.generate.return_value = (TEST_CAPTCHA_TEXT, TEST_CAPTCHA_IMAGE)
        yield instance

@pytest.fixture
def mock_redis():
    with patch("backend.src.core.cache.captcha.redis.Redis") as mock:
        instance = mock.return_value
        instance.setex.return_value = True
        instance.get.return_value = TEST_CAPTCHA_TEXT.upper()
        instance.delete.return_value = True
        yield instance

@pytest.fixture
def mock_captcha_cache(mock_redis):
    with patch("backend.src.core.cache.captcha.CaptchaCache") as mock:
        instance = mock.return_value
        instance.redis = mock_redis
        instance.expire_time = 300
        instance.save_captcha.return_value = True
        instance.verify_captcha.return_value = True
        instance.get_captcha.return_value = TEST_CAPTCHA_TEXT.upper()
        yield instance

@pytest.fixture
def mock_auth_service():
    with patch("backend.src.core.auth.service.auth_service") as mock:
        mock.authenticate_user.return_value = (TEST_USER, TEST_TOKEN)
        yield mock

@pytest.mark.asyncio
class TestCaptcha:
    """验证码相关测试"""
    
    async def test_generate_captcha_success(self):
        """测试成功生成验证码"""
        response = await generate_captcha()
        assert isinstance(response, CaptchaResponse)
        assert response.image == TEST_CAPTCHA_IMAGE
        assert len(response.captcha_id) > 0

    async def test_generate_captcha_failure(self):
        """测试生成验证码失败"""
        with patch("backend.src.api.v1.auth.service.captcha_cache") as mock_cache:
            mock_cache.save_captcha.return_value = False
            with pytest.raises(HTTPException) as exc_info:
                await generate_captcha()
            assert exc_info.value.status_code == 500
            assert exc_info.value.detail == {
                "code": AuthErrorCode.GENERATE_CAPTCHA_FAILED,
                "message": AuthErrorCode.get_message(AuthErrorCode.GENERATE_CAPTCHA_FAILED)
            }

@pytest.mark.asyncio
class TestLogin:
    """登录相关测试"""

    async def test_login_success(self):
        """测试正常登录"""
        response = await verify_login(
            username="test_user",
            password="password",
            captcha_id="test_id",
            captcha_code=TEST_CAPTCHA_TEXT,
            remember=False
        )
        assert isinstance(response, TokenResponse)
        assert response == TEST_TOKEN

    async def test_login_invalid_captcha(self):
        """测试验证码错误"""
        with patch("backend.src.api.v1.auth.service.captcha_cache") as mock_cache:
            mock_cache.verify_captcha.return_value = False
            with pytest.raises(HTTPException) as exc_info:
                await verify_login(
                    username="test_user",
                    password="password",
                    captcha_id="test_id",
                    captcha_code="wrong_code",
                    remember=False
                )
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == {
                "code": AuthErrorCode.INVALID_CAPTCHA,
                "message": AuthErrorCode.get_message(AuthErrorCode.INVALID_CAPTCHA)
            }

    async def test_login_invalid_credentials(self):
        """测试用户名或密码错误"""
        with patch("backend.src.api.v1.auth.service.auth_service") as mock_auth:
            mock_auth.authenticate_user.side_effect = Exception("Invalid credentials")
            with pytest.raises(HTTPException) as exc_info:
                await verify_login(
                    username="wrong_user",
                    password="wrong_password",
                    captcha_id="test_id",
                    captcha_code=TEST_CAPTCHA_TEXT,
                    remember=False
                )
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == {
                "code": AuthErrorCode.INVALID_CREDENTIALS,
                "message": AuthErrorCode.get_message(AuthErrorCode.INVALID_CREDENTIALS)
            }

@pytest.mark.asyncio
class TestTokenRefresh:
    """Token刷新相关测试"""

    async def test_refresh_token_success(self):
        """测试成功刷新token"""
        with patch("backend.src.api.v1.auth.service.refresh_access_token") as mock_refresh:
            mock_refresh.return_value = TEST_TOKEN
            response = await refresh_token("valid_refresh_token")
            assert isinstance(response, TokenResponse)
            assert response == TEST_TOKEN
            mock_refresh.assert_called_once_with("valid_refresh_token")

    async def test_refresh_token_invalid(self):
        """测试无效的刷新token"""
        with patch("backend.src.api.v1.auth.service.refresh_access_token") as mock_refresh:
            mock_refresh.side_effect = Exception("Invalid refresh token")
            with pytest.raises(HTTPException) as exc_info:
                await refresh_token("invalid_refresh_token")
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == {
                "code": AuthErrorCode.INVALID_TOKEN,
                "message": AuthErrorCode.get_message(AuthErrorCode.INVALID_TOKEN)
            }
            mock_refresh.assert_called_once_with("invalid_refresh_token") 