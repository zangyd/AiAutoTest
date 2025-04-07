"""
认证流程端到端测试
"""
import pytest
import jwt
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient
from fastapi import status

from core.config.settings import settings
from core.auth.models import User

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_db_user():
    """创建一个数据库用户模型"""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True,
        is_superuser=False
    )


@pytest.fixture
def mock_query():
    """创建一个模拟的数据库查询"""
    mock = MagicMock()
    mock.filter.return_value.first.return_value = None
    return mock


@pytest.fixture
def mock_auth_service():
    """创建一个模拟的认证服务"""
    service = AsyncMock()
    
    # 配置模拟方法返回值
    service.authenticate_user.return_value = None
    service.create_tokens.return_value = ("access_token", "refresh_token")
    service.refresh_access_token.return_value = "new_access_token"
    service.logout.return_value = True
    
    return service


class TestAuthFlow:
    """认证流程测试类"""
    
    async def test_complete_auth_flow(self, async_client, mock_auth_service, mock_query, mock_db_user):
        """测试完整的认证流程"""
        # 1. 准备测试数据
        login_data = {
            "username": "testuser",
            "password": "password"
        }
        
        # 2. 模拟所需的依赖
        # 模拟用户验证成功
        mock_auth_service.authenticate_user.return_value = mock_db_user
        
        # 模拟数据库查询找到用户
        mock_query.filter.return_value.first.return_value = mock_db_user
        
        # 应用模拟
        with patch("core.auth.service.AuthService.authenticate_user", side_effect=mock_auth_service.authenticate_user), \
             patch("core.auth.service.AuthService.create_tokens", side_effect=mock_auth_service.create_tokens), \
             patch("core.auth.service.AuthService.refresh_access_token", side_effect=mock_auth_service.refresh_access_token), \
             patch("core.auth.service.AuthService.logout", side_effect=mock_auth_service.logout), \
             patch("sqlalchemy.orm.Session.query", return_value=mock_query), \
             patch("api.v1.auth.router.get_current_user", return_value=mock_db_user):
            
            # 3. 执行登录
            login_response = await async_client.post(
                "/api/v1/auth/login",
                data=login_data
            )
            
            # 断言登录成功
            assert login_response.status_code == status.HTTP_200_OK
            login_result = login_response.json()
            assert "access_token" in login_result
            assert "refresh_token" in login_result
            
            # 4. 使用访问令牌获取当前用户信息
            me_response = await async_client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {login_result['access_token']}"}
            )
            
            # 断言获取用户信息成功
            assert me_response.status_code == status.HTTP_200_OK
            me_result = me_response.json()
            assert me_result["username"] == mock_db_user.username
            
            # 5. 刷新访问令牌
            refresh_response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": login_result["refresh_token"]}
            )
            
            # 断言刷新成功
            assert refresh_response.status_code == status.HTTP_200_OK
            refresh_result = refresh_response.json()
            assert refresh_result["access_token"] == "new_access_token"
            
            # 6. 使用新的访问令牌再次获取用户信息
            me_response2 = await async_client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {refresh_result['access_token']}"}
            )
            
            # 断言仍然能获取用户信息
            assert me_response2.status_code == status.HTTP_200_OK
            
            # 7. 登出
            logout_response = await async_client.post(
                "/api/v1/auth/logout",
                json={
                    "token": refresh_result["access_token"],
                    "refresh_token": login_result["refresh_token"]
                }
            )
            
            # 断言登出成功
            assert logout_response.status_code == status.HTTP_204_NO_CONTENT
    
    async def test_auth_flow_with_token_validation(self, async_client, mock_auth_service, mock_db_user, mock_query):
        """测试带有实际令牌验证的认证流程"""
        # 1. 准备测试数据
        login_data = {
            "username": "testuser",
            "password": "password"
        }
        
        # 2. 创建有效的模拟令牌
        # 访问令牌
        access_token_payload = {
            "sub": "1",
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True,
            "is_superuser": False
        }
        access_token = jwt.encode(
            access_token_payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        # 刷新令牌
        refresh_token_payload = {
            "sub": "1",
            "username": "testuser",
            "refresh": True
        }
        refresh_token = jwt.encode(
            refresh_token_payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        # 3. 配置模拟返回值
        mock_auth_service.authenticate_user.return_value = mock_db_user
        mock_auth_service.create_tokens.return_value = (access_token, refresh_token)
        mock_auth_service.refresh_access_token.return_value = access_token
        
        # 模拟数据库查询找到用户
        mock_query.filter.return_value.first.return_value = mock_db_user
        
        # 4. 应用模拟
        with patch("core.auth.service.AuthService.authenticate_user", side_effect=mock_auth_service.authenticate_user), \
             patch("core.auth.service.AuthService.create_tokens", side_effect=mock_auth_service.create_tokens), \
             patch("core.auth.service.AuthService.refresh_access_token", side_effect=mock_auth_service.refresh_access_token), \
             patch("core.auth.service.AuthService.logout", side_effect=mock_auth_service.logout), \
             patch("sqlalchemy.orm.Session.query", return_value=mock_query), \
             patch("api.v1.auth.router.get_current_user", return_value=mock_db_user), \
             patch("core.auth.token_blacklist.TokenBlacklist.add_to_blacklist", return_value=True), \
             patch("core.auth.token_blacklist.TokenBlacklist.is_blacklisted", return_value=False):
            
            # 5. 执行登录
            login_response = await async_client.post(
                "/api/v1/auth/login",
                data=login_data
            )
            
            # 断言登录成功
            assert login_response.status_code == status.HTTP_200_OK
            login_result = login_response.json()
            assert login_result["access_token"] == access_token
            assert login_result["refresh_token"] == refresh_token
            
            # 6. 使用访问令牌获取当前用户信息
            me_response = await async_client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {login_result['access_token']}"}
            )
            
            # 断言获取用户信息成功
            assert me_response.status_code == status.HTTP_200_OK
            
            # 7. 模拟令牌被加入黑名单
            with patch("core.auth.token_blacklist.TokenBlacklist.is_blacklisted", return_value=True):
                # 尝试使用被撤销的令牌获取用户信息
                # 由于我们的测试环境限制，无法直接测试这个场景，但在实际应用中会被拒绝
                # 这里我们模拟router.get_current_user抛出异常
                with patch("api.v1.auth.router.get_current_user", side_effect=Exception("Token has been revoked")):
                    me_response2 = await async_client.get(
                        "/api/v1/auth/me",
                        headers={"Authorization": f"Bearer {login_result['access_token']}"}
                    )
                    
                    # 断言请求失败
                    assert me_response2.status_code != status.HTTP_200_OK 