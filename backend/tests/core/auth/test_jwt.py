import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from fastapi import HTTPException
import jwt

from src.core.auth.jwt import JWTHandler
from src.core.config.jwt_config import jwt_settings


@pytest.fixture
def jwt_handler():
    """创建JWT处理器实例"""
    return JWTHandler()


@pytest.fixture
def mock_redis():
    """创建Mock的Redis客户端"""
    return Mock()


def test_create_access_token(jwt_handler):
    """测试创建访问令牌"""
    data = {"sub": "test_user"}
    token = jwt_handler.create_access_token(data)
    
    # 验证令牌
    payload = jwt.decode(
        token,
        jwt_settings.SECRET_KEY,
        algorithms=[jwt_settings.ALGORITHM]
    )
    
    assert payload["sub"] == "test_user"
    assert "exp" in payload


def test_create_refresh_token(jwt_handler):
    """测试创建刷新令牌"""
    data = {"sub": "test_user"}
    token = jwt_handler.create_refresh_token(data)
    
    # 验证令牌
    payload = jwt.decode(
        token,
        jwt_settings.SECRET_KEY,
        algorithms=[jwt_settings.ALGORITHM]
    )
    
    assert payload["sub"] == "test_user"
    assert payload["refresh"] is True
    assert "exp" in payload


def test_verify_token_valid(jwt_handler):
    """测试验证有效令牌"""
    data = {"sub": "test_user"}
    token = jwt_handler.create_access_token(data)
    
    # 验证令牌
    payload = jwt_handler.verify_token(token)
    assert payload["sub"] == "test_user"


def test_verify_token_expired(jwt_handler):
    """测试验证过期令牌"""
    # 创建一个已过期的令牌
    data = {
        "sub": "test_user",
        "exp": datetime.utcnow() - timedelta(minutes=1)
    }
    token = jwt.encode(
        data,
        jwt_settings.SECRET_KEY,
        algorithm=jwt_settings.ALGORITHM
    )
    
    # 验证令牌应该抛出异常
    with pytest.raises(HTTPException) as exc_info:
        jwt_handler.verify_token(token)
    assert exc_info.value.status_code == 401
    assert "Token has expired" in exc_info.value.detail


def test_verify_token_invalid(jwt_handler):
    """测试验证无效令牌"""
    # 使用错误的密钥创建令牌
    data = {"sub": "test_user"}
    token = jwt.encode(
        data,
        "wrong_secret_key",
        algorithm=jwt_settings.ALGORITHM
    )
    
    # 验证令牌应该抛出异常
    with pytest.raises(HTTPException) as exc_info:
        jwt_handler.verify_token(token)
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail


def test_revoke_token(jwt_handler, mock_redis):
    """测试令牌加入黑名单"""
    # 创建带有Redis客户端的处理器
    handler = JWTHandler(redis_client=mock_redis)
    
    # 创建令牌
    data = {"sub": "test_user"}
    token = handler.create_access_token(data)
    
    # 将令牌加入黑名单
    handler.revoke_token(token)
    
    # 验证Redis调用
    mock_redis.setex.assert_called_once()
    args = mock_redis.setex.call_args[0]
    assert args[0] == f"blacklist:{token}"
    assert isinstance(args[1], int)
    assert args[2] == "revoked"


def test_verify_revoked_token(jwt_handler, mock_redis):
    """测试验证已撤销的令牌"""
    # 创建带有Redis客户端的处理器
    handler = JWTHandler(redis_client=mock_redis)
    
    # 创建令牌
    data = {"sub": "test_user"}
    token = handler.create_access_token(data)
    
    # 模拟令牌在黑名单中
    mock_redis.get.return_value = "revoked"
    
    # 验证令牌应该抛出异常
    with pytest.raises(HTTPException) as exc_info:
        handler.verify_token(token)
    assert exc_info.value.status_code == 401
    assert "Token has been revoked" in exc_info.value.detail 