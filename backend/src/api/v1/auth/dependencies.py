"""
认证相关的依赖项
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from core.auth.jwt import decode_token
from core.auth.schemas import UserOut
from core.database import get_session
from models.user import User
from .constants import AuthErrorCode

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_token(
    request: Request,
    token: str = Depends(oauth2_scheme)
) -> str:
    """
    获取当前token
    
    Args:
        request: 请求对象
        token: 访问令牌
        
    Returns:
        str: 当前token
        
    Raises:
        HTTPException: token无效时抛出异常
    """
    return token

async def get_current_user(
    token: str = Depends(get_current_token),
    db = Depends(get_session)
) -> UserOut:
    """
    获取当前用户
    
    Args:
        token: 访问令牌
        db: 数据库会话
        
    Returns:
        UserOut: 当前用户信息
        
    Raises:
        HTTPException: 用户验证失败时抛出异常
    """
    try:
        payload = await decode_token(token)
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": AuthErrorCode.INVALID_TOKEN.code,
                    "message": AuthErrorCode.INVALID_TOKEN.message
                }
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": AuthErrorCode.INVALID_TOKEN.code,
                "message": AuthErrorCode.INVALID_TOKEN.message
            }
        )
        
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": AuthErrorCode.USER_NOT_FOUND.code,
                "message": AuthErrorCode.USER_NOT_FOUND.message
            }
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": AuthErrorCode.USER_INACTIVE.code,
                "message": AuthErrorCode.USER_INACTIVE.message
            }
        )
        
    return UserOut.from_orm(user)

async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db = Depends(get_session)
) -> Optional[UserOut]:
    """
    获取可选的当前用户
    
    Args:
        token: 访问令牌
        db: 数据库会话
        
    Returns:
        Optional[UserOut]: 当前用户信息，如果未登录则返回None
    """
    if not token:
        return None
        
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None 