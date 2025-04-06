"""
认证路由测试
"""
import pytest
from unittest.mock import patch
from fastapi import status
from ..schemas import CaptchaResponse, TokenResponse
from .test_auth import TEST_USER, TEST_TOKEN

class TestAuthRouter:
    """认证路由测试类"""

    def test_get_captcha(self, client):
        """测试获取验证码接口"""
        with patch("..service.generate_captcha") as mock_generate:
            mock_generate.return_value = CaptchaResponse(
                captcha_id="test_id",
                image="base64_image_data"
            )
            response = client.get("/auth/captcha")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["captcha_id"] == "test_id"
            assert data["image"] == "base64_image_data"

    def test_login_success(self, client):
        """测试登录接口 - 成功场景"""
        with patch("..service.verify_login") as mock_verify:
            mock_verify.return_value = TEST_TOKEN
            response = client.post("/auth/login", json={
                "username": "test_user",
                "password": "password",
                "captcha_id": "test_id",
                "captcha_code": "1234",
                "remember": False
            })
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["access_token"] == TEST_TOKEN.access_token
            assert data["refresh_token"] == TEST_TOKEN.refresh_token

    def test_login_invalid_input(self, client):
        """测试登录接口 - 无效输入"""
        response = client.post("/auth/login", json={
            "username": "test_user",
            # 缺少必要字段
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_refresh_token_success(self, client):
        """测试刷新令牌接口 - 成功场景"""
        with patch("..service.refresh_token") as mock_refresh:
            mock_refresh.return_value = TEST_TOKEN
            response = client.post("/auth/refresh", json={
                "refresh_token": "valid_refresh_token"
            })
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["access_token"] == TEST_TOKEN.access_token

    def test_refresh_token_invalid(self, client):
        """测试刷新令牌接口 - 无效令牌"""
        with patch("..service.refresh_token") as mock_refresh:
            mock_refresh.side_effect = Exception("Invalid token")
            response = client.post("/auth/refresh", json={
                "refresh_token": "invalid_refresh_token"
            })
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_info(self, client):
        """测试获取用户信息接口"""
        with patch("....core.auth.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = TEST_USER
            response = client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {TEST_TOKEN.access_token}"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["username"] == TEST_USER.username
            assert data["email"] == TEST_USER.email

    def test_get_user_info_unauthorized(self, client):
        """测试获取用户信息接口 - 未授权"""
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 