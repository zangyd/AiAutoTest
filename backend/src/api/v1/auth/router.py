"""
认证相关的路由定义
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any

from backend.src.core.auth.service import auth_service
from backend.src.core.auth.dependencies import get_current_user, refresh_access_token
from backend.src.core.auth.schemas import UserOut, TokenResponse

router = APIRouter(prefix="/auth", tags=["认证"])

@router.get("/captcha", response_model=CaptchaResponse)
async def get_captcha() -> CaptchaResponse:
    """
    获取验证码
    
    Returns:
        CaptchaResponse: 验证码信息
    """
    return await generate_captcha()

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    remember: bool = False
) -> TokenResponse:
    """
    用户登录
    
    Args:
        form_data: OAuth2表单数据
        remember: 是否记住登录状态
        
    Returns:
        TokenResponse: 令牌信息
        
    Raises:
        HTTPException: 登录失败时抛出异常
    """
    user, token = await auth_service.authenticate_user(form_data, remember)
    return token

@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str) -> TokenResponse:
    """
    刷新访问令牌
    
    Args:
        refresh_token: 刷新令牌
        
    Returns:
        TokenResponse: 新的令牌信息
        
    Raises:
        HTTPException: 刷新失败时抛出异常
    """
    return await refresh_access_token(refresh_token)

@router.get("/me", response_model=UserOut)
async def get_user_info(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户依赖
        
    Returns:
        UserOut: 用户信息
    """
    return current_user 