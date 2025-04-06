"""
认证依赖测试模块
"""
import pytest
from fastapi import HTTPException
from unittest.mock import patch

from ..dependencies import get_current_user, get_current_active_user, refresh_access_token
from ..schemas import UserOut, TokenResponse
from ..jwt import create_access_token, create_refresh_token

@pytest.mark.asyncio
async def test_get_current_user_success():
    """测试获取当前用户成功"""
    # 创建测试令牌
    user_id = "1"
    token = create_access_token({"sub": user_id})
    
    # 测试获取当前用户
    user = await get_current_user(token)
    
    assert isinstance(user, UserOut)
    assert user.id == 1
    assert user.username == "test_user"
    assert user.is_active is True

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """测试获取当前用户失败 - 无效令牌"""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid_token")
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "无效的令牌"

@pytest.mark.asyncio
async def test_get_current_user_missing_sub():
    """测试获取当前用户失败 - 缺少用户ID"""
    # 创建不包含sub的令牌
    token = create_access_token({})
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "无效的认证信息"

@pytest.mark.asyncio
async def test_get_current_active_user_success():
    """测试获取当前活跃用户成功"""
    user = UserOut(
        id=1,
        username="test_user",
        email="test@example.com",
        is_active=True,
        is_superuser=False
    )
    
    active_user = await get_current_active_user(user)
    assert active_user == user

@pytest.mark.asyncio
async def test_get_current_active_user_inactive():
    """测试获取当前活跃用户失败 - 用户未激活"""
    user = UserOut(
        id=1,
        username="test_user",
        email="test@example.com",
        is_active=False,
        is_superuser=False
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(user)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "用户未激活"

@pytest.mark.asyncio
async def test_refresh_access_token_success():
    """测试刷新访问令牌成功"""
    # 创建刷新令牌
    user_id = "1"
    refresh_token = create_refresh_token({"sub": user_id})
    
    # 测试刷新令牌
    token_response = await refresh_access_token(refresh_token)
    
    assert isinstance(token_response, TokenResponse)
    assert token_response.token_type == "bearer"
    assert token_response.access_token is not None
    assert token_response.refresh_token is not None
    assert token_response.expires_in == 3600

@pytest.mark.asyncio
async def test_refresh_access_token_invalid():
    """测试刷新访问令牌失败 - 无效的刷新令牌"""
    with pytest.raises(HTTPException) as exc_info:
        await refresh_access_token("invalid_token")
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "无效的令牌"

@pytest.mark.asyncio
async def test_refresh_access_token_wrong_type():
    """测试刷新访问令牌失败 - 错误的令牌类型"""
    # 创建访问令牌而不是刷新令牌
    token = create_access_token({"sub": "1"})
    
    with pytest.raises(HTTPException) as exc_info:
        await refresh_access_token(token)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "无效的刷新令牌" 