from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from .jwt import jwt_handler
from ..config.jwt_config import jwt_settings
from ...api.models import UserOut
from ...api.base import StatusEnum

# 模拟用户数据库
mock_users_db = {
    "admin": UserOut(
        id=1,
        username="admin",
        email="admin@example.com",
        department="技术部",
        position="管理员",
        status=StatusEnum.ACTIVE,
        permissions=["admin", "user_view", "user_manage"]
    ),
    "test_user": UserOut(
        id=2,
        username="test_user",
        email="test@example.com",
        department="技术部",
        position="工程师",
        status=StatusEnum.ACTIVE,
        permissions=["user_view"]
    )
}

# OAuth2密码流的令牌URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserOut:
    """
    获取当前用户
    
    Args:
        token: JWT令牌
        
    Returns:
        UserOut: 用户信息
        
    Raises:
        HTTPException: 当认证失败时
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 验证令牌
        payload = jwt_handler.verify_token(token)
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        # 从模拟数据库获取用户信息
        user = mock_users_db.get(username)
        if user is None:
            raise credentials_exception
            
        return user
    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user: UserOut = Depends(get_current_user)
) -> UserOut:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        UserOut: 用户信息
        
    Raises:
        HTTPException: 当用户被禁用时
    """
    # 这里可以添加检查用户状态的逻辑
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 