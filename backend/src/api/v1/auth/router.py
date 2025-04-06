"""
认证相关的路由定义
"""
from fastapi import APIRouter, Depends
from typing import Any

from .schemas import (
    CaptchaResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest
)
from .service import (
    generate_captcha,
    verify_login,
    refresh_token
)
from ....core.auth.dependencies import get_current_user
from ...models import UserOut

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
async def login(login_data: LoginRequest) -> TokenResponse:
    """
    用户登录
    
    Args:
        login_data: 登录请求数据
        
    Returns:
        TokenResponse: 令牌信息
    """
    return await verify_login(
        username=login_data.username,
        password=login_data.password,
        captcha_id=login_data.captcha_id,
        captcha_code=login_data.captcha_code,
        remember=login_data.remember
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_request: RefreshTokenRequest) -> TokenResponse:
    """
    刷新访问令牌
    
    Args:
        refresh_request: 刷新令牌请求
        
    Returns:
        TokenResponse: 新的令牌信息
    """
    return await refresh_token(refresh_request.refresh_token)

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