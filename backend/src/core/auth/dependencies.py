from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from .jwt import jwt_handler
from ..config.jwt_config import jwt_settings

# OAuth2密码流的令牌URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    获取当前用户
    
    Args:
        token: JWT令牌
        
    Returns:
        dict: 用户信息
        
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
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # 这里可以添加从数据库获取用户信息的逻辑
        # user = await get_user(user_id)
        # if user is None:
        #     raise credentials_exception
        # return user
        
        return {"user_id": user_id}
    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        dict: 用户信息
        
    Raises:
        HTTPException: 当用户被禁用时
    """
    # 这里可以添加检查用户状态的逻辑
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 