"""
认证依赖模块

提供FastAPI依赖注入使用的认证相关函数
"""
from typing import Optional, Tuple

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .service import auth_service
from ...api.models import UserOut, TokenResponse
from ...api.exceptions import AuthenticationError

# OAuth2密码流的令牌URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def authenticate_user(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Tuple[UserOut, TokenResponse]:
    """
    用户认证依赖
    
    Args:
        form_data: OAuth2密码表单数据
        
    Returns:
        Tuple[UserOut, TokenResponse]: 用户信息和令牌
        
    Raises:
        HTTPException: 认证失败时
    """
    try:
        return auth_service.authenticate_user(form_data)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> UserOut:
    """
    获取当前用户依赖
    
    Args:
        token: JWT令牌
        
    Returns:
        UserOut: 用户信息
        
    Raises:
        HTTPException: 认证失败时
    """
    try:
        return auth_service.verify_token(token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(
    current_user: UserOut = Depends(get_current_user)
) -> UserOut:
    """
    获取当前活跃用户依赖
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        UserOut: 用户信息
        
    Raises:
        HTTPException: 用户被禁用时
    """
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return current_user

async def refresh_access_token(
    refresh_token: str
) -> TokenResponse:
    """
    刷新访问令牌依赖
    
    Args:
        refresh_token: 刷新令牌
        
    Returns:
        TokenResponse: 新的令牌信息
        
    Raises:
        HTTPException: 刷新令牌验证失败时
    """
    try:
        return auth_service.refresh_access_token(refresh_token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) 