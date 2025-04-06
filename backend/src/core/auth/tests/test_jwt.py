"""
JWT令牌处理模块测试
"""
import pytest
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException

from ..jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
    SECRET_KEY,
    ALGORITHM
)

def test_create_access_token_success():
    """测试成功创建访问令牌"""
    data = {"sub": "1"}
    token = create_access_token(data)
    
    # 验证令牌
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "1"
    assert payload["type"] == "access"
    assert "exp" in payload

def test_create_refresh_token_success():
    """测试成功创建刷新令牌"""
    data = {"sub": "1"}
    token = create_refresh_token(data)
    
    # 验证令牌
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "1"
    assert payload["type"] == "refresh"
    assert "exp" in payload

def test_verify_token_success():
    """测试成功验证令牌"""
    data = {"sub": "1", "exp": datetime.utcnow() + timedelta(minutes=30)}
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    
    payload = verify_token(token)
    assert payload["sub"] == "1"

def test_verify_token_expired():
    """测试过期令牌验证"""
    data = {"sub": "1", "exp": datetime.utcnow() - timedelta(minutes=1)}
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    
    with pytest.raises(HTTPException) as exc_info:
        verify_token(token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "令牌已过期"

def test_verify_token_invalid():
    """测试无效令牌验证"""
    with pytest.raises(HTTPException) as exc_info:
        verify_token("invalid_token")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "无效的令牌" 