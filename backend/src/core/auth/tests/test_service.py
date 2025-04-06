"""
认证服务测试模块
"""
import pytest
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..service import AuthService, auth_service
from ..schemas import UserOut, TokenResponse

@pytest.fixture
def auth_form_data():
    """创建测试用的表单数据"""
    form_data = OAuth2PasswordRequestForm(
        username="test_user",
        password="password",
        scope=""
    )
    return form_data

@pytest.mark.asyncio
async def test_authenticate_user_success(auth_form_data):
    """测试用户认证成功"""
    # 使用正确的测试用户数据
    auth_form_data.username = "test_user"
    auth_form_data.password = "password"
    
    user, token = await auth_service.authenticate_user(auth_form_data)
    
    # 验证用户信息
    assert isinstance(user, UserOut)
    assert user.username == "test_user"
    assert user.is_active is True
    
    # 验证令牌信息
    assert isinstance(token, TokenResponse)
    assert token.token_type == "bearer"
    assert token.access_token is not None
    assert token.refresh_token is not None
    assert token.expires_in == 3600

@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials(auth_form_data):
    """测试用户认证失败 - 无效的凭证"""
    # 使用错误的密码
    auth_form_data.username = "test_user"
    auth_form_data.password = "wrong_password"
    
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.authenticate_user(auth_form_data)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "用户名或密码错误"

@pytest.mark.asyncio
async def test_authenticate_user_with_remember(auth_form_data):
    """测试用户认证 - 记住登录"""
    auth_form_data.username = "test_user"
    auth_form_data.password = "password"
    
    user, token = await auth_service.authenticate_user(
        auth_form_data,
        remember=True
    )
    
    # 验证用户信息
    assert isinstance(user, UserOut)
    assert user.username == "test_user"
    
    # 验证令牌信息
    assert isinstance(token, TokenResponse)
    assert token.token_type == "bearer"
    assert token.access_token is not None
    assert token.refresh_token is not None 