"""
认证路由模块

提供认证相关的API端点
"""
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from ...core.auth.dependencies import (
    authenticate_user,
    get_current_user,
    refresh_access_token
)
from ..models import UserOut, TokenResponse, RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/login", response_model=TokenResponse)
async def login(
    user_and_token: tuple[UserOut, TokenResponse] = Depends(authenticate_user)
) -> TokenResponse:
    """
    用户登录
    
    Args:
        user_and_token: 用户认证依赖返回的用户信息和令牌
        
    Returns:
        TokenResponse: 令牌信息
    """
    _, token = user_and_token
    return token

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest
) -> TokenResponse:
    """
    刷新访问令牌
    
    Args:
        refresh_request: 刷新令牌请求
        
    Returns:
        TokenResponse: 新的令牌信息
    """
    return await refresh_access_token(refresh_request.refresh_token)

@router.get("/me", response_model=UserOut)
async def get_user_info(
    current_user: UserOut = Depends(get_current_user)
) -> UserOut:
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户依赖
        
    Returns:
        UserOut: 用户信息
    """
    return current_user 