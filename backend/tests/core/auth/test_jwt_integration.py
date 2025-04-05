import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock

import jwt
from fastapi import HTTPException
from redis import Redis

from src.core.auth.jwt import JWTHandler
from src.core.config.jwt_config import jwt_settings, JWTSettings
from src.core.auth.dependencies import get_current_user, get_current_active_user

# 测试数据
TEST_USER_ID = "test_user_123"
TEST_USER_DATA = {
    "sub": TEST_USER_ID,
    "username": "testuser",
    "email": "test@example.com"
}

@pytest.fixture
def jwt_settings_test():
    """测试用JWT设置"""
    return JWTSettings(
        SECRET_KEY="test-secret-key",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=5,
        REFRESH_TOKEN_EXPIRE_DAYS=1
    )

@pytest.fixture
def mock_redis():
    """模拟Redis客户端"""
    redis_mock = Mock(spec=Redis)
    redis_mock.get.return_value = None
    return redis_mock

@pytest.fixture
def jwt_handler(mock_redis):
    """创建JWT处理器实例"""
    return JWTHandler(redis_client=mock_redis)

class TestJWTConfig:
    """测试JWT配置"""
    
    def test_jwt_settings(self, jwt_settings_test):
        """测试JWT设置是否正确"""
        assert jwt_settings_test.SECRET_KEY == "test-secret-key"
        assert jwt_settings_test.ALGORITHM == "HS256"
        assert jwt_settings_test.ACCESS_TOKEN_EXPIRE_MINUTES == 5
        assert jwt_settings_test.REFRESH_TOKEN_EXPIRE_DAYS == 1
        assert jwt_settings_test.TOKEN_TYPE == "bearer"
        
    def test_expiration_times(self, jwt_settings_test):
        """测试过期时间计算"""
        assert jwt_settings_test.access_token_expires == timedelta(minutes=5)
        assert jwt_settings_test.refresh_token_expires == timedelta(days=1)
        assert jwt_settings_test.blacklist_expires == timedelta(hours=24)

class TestTokenGeneration:
    """测试令牌生成"""
    
    def test_access_token_generation(self, jwt_handler):
        """测试访问令牌生成"""
        token = jwt_handler.create_access_token(TEST_USER_DATA)
        payload = jwt.decode(
            token,
            jwt_settings.SECRET_KEY,
            algorithms=[jwt_settings.ALGORITHM]
        )
        
        assert payload["sub"] == TEST_USER_ID
        assert "exp" in payload
        assert payload["username"] == "testuser"
        
    def test_refresh_token_generation(self, jwt_handler):
        """测试刷新令牌生成"""
        token = jwt_handler.create_refresh_token(TEST_USER_DATA)
        payload = jwt.decode(
            token,
            jwt_settings.SECRET_KEY,
            algorithms=[jwt_settings.ALGORITHM]
        )
        
        assert payload["sub"] == TEST_USER_ID
        assert payload["refresh"] is True
        assert "exp" in payload

class TestTokenValidation:
    """测试令牌验证"""
    
    def test_valid_token(self, jwt_handler):
        """测试有效令牌验证"""
        token = jwt_handler.create_access_token(TEST_USER_DATA)
        payload = jwt_handler.verify_token(token)
        assert payload["sub"] == TEST_USER_ID
        
    def test_expired_token(self, jwt_handler):
        """测试过期令牌"""
        expired_data = TEST_USER_DATA.copy()
        expired_data["exp"] = datetime.utcnow() - timedelta(minutes=1)
        token = jwt.encode(
            expired_data,
            jwt_settings.SECRET_KEY,
            algorithm=jwt_settings.ALGORITHM
        )
        
        with pytest.raises(HTTPException) as exc:
            jwt_handler.verify_token(token)
        assert exc.value.status_code == 401
        assert "Token has expired" in exc.value.detail
        
    def test_invalid_token(self, jwt_handler):
        """测试无效令牌"""
        invalid_token = "invalid.token.string"
        with pytest.raises(HTTPException) as exc:
            jwt_handler.verify_token(invalid_token)
        assert exc.value.status_code == 401
        assert "Could not validate credentials" in exc.value.detail

class TestTokenBlacklist:
    """测试令牌黑名单"""
    
    def test_token_revocation(self, jwt_handler, mock_redis):
        """测试令牌撤销"""
        token = jwt_handler.create_access_token(TEST_USER_DATA)
        jwt_handler.revoke_token(token)
        
        # 验证Redis调用
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args[0]
        assert call_args[0] == f"blacklist:{token}"
        assert isinstance(call_args[1], int)
        assert call_args[2] == "revoked"
        
    def test_revoked_token_validation(self, jwt_handler, mock_redis):
        """测试已撤销令牌的验证"""
        token = jwt_handler.create_access_token(TEST_USER_DATA)
        mock_redis.get.return_value = "revoked"
        
        with pytest.raises(HTTPException) as exc:
            jwt_handler.verify_token(token)
        assert exc.value.status_code == 401
        assert "Token has been revoked" in exc.value.detail

class TestAuthenticationDependencies:
    """测试认证依赖"""
    
    async def test_get_current_user(self, jwt_handler):
        """测试获取当前用户"""
        token = jwt_handler.create_access_token(TEST_USER_DATA)
        user = await get_current_user(token)
        assert user["user_id"] == TEST_USER_ID
        
    async def test_get_current_active_user(self, jwt_handler):
        """测试获取当前活跃用户"""
        token = jwt_handler.create_access_token(TEST_USER_DATA)
        current_user = {"user_id": TEST_USER_ID, "is_active": True}
        user = await get_current_active_user(current_user)
        assert user["user_id"] == TEST_USER_ID 