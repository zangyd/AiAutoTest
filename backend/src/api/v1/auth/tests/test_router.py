"""
认证路由测试
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from backend.src.api.v1.auth.schemas import CaptchaResponse, TokenResponse
from backend.src.api.v1.auth.constants import AuthErrorCode
from .test_auth import TEST_USER, TEST_TOKEN, TEST_CAPTCHA_TEXT, TEST_CAPTCHA_IMAGE

class TestAuthRouter:
    """认证路由测试类"""

    def test_get_captcha(self, client):
        """测试获取验证码接口"""
        with patch("backend.src.api.v1.auth.service.generate_captcha") as mock_generate:
            mock_generate.return_value = CaptchaResponse(
                captcha_id="test_id",
                image=TEST_CAPTCHA_IMAGE
            )
            response = client.get("/auth/captcha")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["code"] == 200
            assert data["message"] == "验证码生成成功"
            assert isinstance(data["data"]["captcha_id"], str)
            assert data["data"]["image"] == TEST_CAPTCHA_IMAGE

    def test_get_captcha_failure(self, client):
        """测试获取验证码失败"""
        with patch("backend.src.api.v1.auth.service.generate_captcha") as mock_generate:
            mock_generate.side_effect = Exception("生成失败")
            response = client.get("/auth/captcha")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["detail"]["code"] == AuthErrorCode.GENERATE_CAPTCHA_FAILED
            assert data["detail"]["message"] == AuthErrorCode.get_message(AuthErrorCode.GENERATE_CAPTCHA_FAILED)

    def test_login_success(self, client):
        """测试登录接口 - 成功场景"""
        with patch("backend.src.api.v1.auth.service.verify_login") as mock_verify:
            mock_verify.return_value = TEST_TOKEN
            response = client.post(
                "/auth/login",
                json={
                    "username": "test_user",
                    "password": "password123",
                    "captcha_id": "test_id",
                    "captcha_code": TEST_CAPTCHA_TEXT,
                    "remember": False
                }
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["code"] == 200
            assert data["message"] == "登录成功"
            assert data["data"]["access_token"] == TEST_TOKEN.access_token
            assert data["data"]["refresh_token"] == TEST_TOKEN.refresh_token

    def test_login_invalid_input(self, client):
        """测试登录接口 - 无效输入"""
        response = client.post("/auth/login", json={
            "username": "test_user",
            # 缺少必要字段
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_invalid_credentials(self, client):
        """测试登录接口 - 无效凭证"""
        with patch("backend.src.api.v1.auth.service.verify_login") as mock_verify:
            mock_verify.side_effect = Exception("Invalid credentials")
            response = client.post(
                "/auth/login",
                json={
                    "username": "wrong_user",
                    "password": "wrong_password",
                    "captcha_id": "test_id",
                    "captcha_code": TEST_CAPTCHA_TEXT,
                    "remember": False
                }
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"]["code"] == AuthErrorCode.INVALID_CREDENTIALS
            assert data["detail"]["message"] == AuthErrorCode.get_message(AuthErrorCode.INVALID_CREDENTIALS)

    def test_refresh_token_success(self, client):
        """测试刷新令牌接口 - 成功场景"""
        with patch("backend.src.api.v1.auth.service.refresh_token") as mock_refresh:
            mock_refresh.return_value = TEST_TOKEN
            response = client.post(
                "/auth/refresh",
                json={"refresh_token": "valid_refresh_token"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["code"] == 200
            assert data["message"] == "令牌刷新成功"
            assert data["data"]["access_token"] == TEST_TOKEN.access_token
            assert data["data"]["refresh_token"] == TEST_TOKEN.refresh_token

    def test_refresh_token_invalid(self, client):
        """测试刷新令牌接口 - 无效令牌"""
        with patch("backend.src.api.v1.auth.service.refresh_token") as mock_refresh:
            mock_refresh.side_effect = Exception("Invalid token")
            response = client.post(
                "/auth/refresh",
                json={"refresh_token": "invalid_refresh_token"}
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"]["code"] == AuthErrorCode.INVALID_TOKEN
            assert data["detail"]["message"] == AuthErrorCode.get_message(AuthErrorCode.INVALID_TOKEN)

    def test_get_user_info(self, client):
        """测试获取用户信息接口"""
        with patch("backend.src.core.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = TEST_USER
            response = client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {TEST_TOKEN.access_token}"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["code"] == 200
            assert data["message"] == "获取用户信息成功"
            assert data["data"]["username"] == TEST_USER.username
            assert data["data"]["email"] == TEST_USER.email

    def test_get_user_info_unauthorized(self, client):
        """测试获取用户信息接口 - 未授权"""
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 