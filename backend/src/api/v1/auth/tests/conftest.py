"""
测试配置文件
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.src.core.auth.schemas import TokenResponse, UserOut
from backend.src.api.v1.auth.router import router
from backend.src.api.v1.auth.tests.test_auth import TEST_USER, TEST_TOKEN, TEST_CAPTCHA_TEXT, TEST_CAPTCHA_IMAGE

@pytest.fixture
def app():
    """创建测试应用"""
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return TestClient(app)

@pytest.fixture(autouse=True)
async def mock_services():
    """Mock所有服务"""
    with (
        patch("backend.src.api.v1.auth.service.captcha_generator") as mock_generator,
        patch("backend.src.api.v1.auth.service.captcha_cache") as mock_cache,
        patch("backend.src.api.v1.auth.service.auth_service") as mock_auth,
        patch("backend.src.api.v1.auth.service.refresh_access_token") as mock_refresh,
        patch("backend.src.core.auth.jwt.create_access_token") as mock_create_access,
        patch("backend.src.core.auth.jwt.create_refresh_token") as mock_create_refresh,
        patch("backend.src.core.auth.jwt.verify_token") as mock_verify
    ):
        # 配置验证码生成器
        mock_generator.generate.return_value = (TEST_CAPTCHA_TEXT, TEST_CAPTCHA_IMAGE)
        
        # 配置验证码缓存
        mock_cache.save_captcha.return_value = True
        mock_cache.verify_captcha.return_value = True
        
        # 配置认证服务
        mock_auth.authenticate_user = AsyncMock(return_value=TEST_USER)
        mock_auth.create_access_token = AsyncMock(return_value=TEST_TOKEN)
        
        # 配置token刷新
        mock_refresh.return_value = TEST_TOKEN
        
        # 配置JWT
        mock_create_access.return_value = TEST_TOKEN.access_token
        mock_create_refresh.return_value = TEST_TOKEN.refresh_token
        mock_verify.return_value = {"sub": "1", "type": "refresh"}
        
        yield {
            "captcha_generator": mock_generator,
            "captcha_cache": mock_cache,
            "auth_service": mock_auth,
            "refresh_token": mock_refresh,
            "create_access_token": mock_create_access,
            "create_refresh_token": mock_create_refresh,
            "verify_token": mock_verify
        } 