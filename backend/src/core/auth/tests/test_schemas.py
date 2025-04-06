"""
认证数据模型测试模块
"""
import pytest
from pydantic import ValidationError

from ..schemas import UserOut, TokenResponse

def test_user_out_valid():
    """测试有效的用户输出模型"""
    user_data = {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
        "is_active": True,
        "is_superuser": False
    }
    
    user = UserOut(**user_data)
    
    assert user.id == user_data["id"]
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]
    assert user.is_active == user_data["is_active"]
    assert user.is_superuser == user_data["is_superuser"]

def test_user_out_invalid_email():
    """测试无效邮箱的用户输出模型"""
    user_data = {
        "id": 1,
        "username": "test_user",
        "email": "invalid_email",  # 无效的邮箱格式
        "is_active": True,
        "is_superuser": False
    }
    
    with pytest.raises(ValidationError) as exc_info:
        UserOut(**user_data)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("email",)
    assert "value is not a valid email address" in errors[0]["msg"]

def test_token_response_valid():
    """测试有效的令牌响应模型"""
    token_data = {
        "access_token": "access_token_value",
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": "refresh_token_value"
    }
    
    token = TokenResponse(**token_data)
    
    assert token.access_token == token_data["access_token"]
    assert token.token_type == token_data["token_type"]
    assert token.expires_in == token_data["expires_in"]
    assert token.refresh_token == token_data["refresh_token"]

def test_token_response_invalid_type():
    """测试无效令牌类型的令牌响应模型"""
    token_data = {
        "access_token": "access_token_value",
        "token_type": "invalid_type",  # 无效的令牌类型
        "expires_in": 3600,
        "refresh_token": "refresh_token_value"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        TokenResponse(**token_data)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("token_type",)

def test_token_response_invalid_expires():
    """测试无效过期时间的令牌响应模型"""
    token_data = {
        "access_token": "access_token_value",
        "token_type": "bearer",
        "expires_in": -1,  # 无效的过期时间
        "refresh_token": "refresh_token_value"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        TokenResponse(**token_data)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("expires_in",)
    assert "Input should be greater than 0" in errors[0]["msg"] 