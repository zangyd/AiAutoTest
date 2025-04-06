"""
认证相关的路由定义
"""
import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any

from backend.src.core.auth.service import auth_service
from backend.src.core.auth.dependencies import get_current_user, refresh_access_token
from backend.src.core.auth.schemas import UserOut, TokenResponse
from .schemas import CaptchaResponse, Response
from .service import generate_captcha
from .constants import AuthErrorCode

router = APIRouter(prefix="/auth", tags=["认证"])

@router.get("/captcha", response_model=Response[CaptchaResponse])
async def get_captcha() -> Response[CaptchaResponse]:
    """
    获取验证码
    
    Returns:
        Response[CaptchaResponse]: 标准响应格式的验证码信息
        
    Raises:
        HTTPException: 验证码生成失败时抛出异常
    """
    try:
        result = await generate_captcha()
        return Response(
            code=200,
            message="验证码生成成功",
            data=result,
            request_id=str(uuid.uuid4()),
            timestamp=int(time.time() * 1000)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": AuthErrorCode.GENERATE_CAPTCHA_FAILED,
                "message": AuthErrorCode.get_message(AuthErrorCode.GENERATE_CAPTCHA_FAILED)
            }
        )

@router.post("/login", response_model=Response[TokenResponse])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    remember: bool = False
) -> Response[TokenResponse]:
    """
    用户登录
    
    Args:
        form_data: OAuth2表单数据
        remember: 是否记住登录状态
        
    Returns:
        Response[TokenResponse]: 标准响应格式的令牌信息
        
    Raises:
        HTTPException: 登录失败时抛出异常
    """
    try:
        user, token = await auth_service.authenticate_user(form_data, remember)
        return Response(
            code=200,
            message="登录成功",
            data=token,
            request_id=str(uuid.uuid4()),
            timestamp=int(time.time() * 1000)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": AuthErrorCode.INVALID_CREDENTIALS,
                "message": AuthErrorCode.get_message(AuthErrorCode.INVALID_CREDENTIALS)
            }
        )

@router.post("/refresh", response_model=Response[TokenResponse])
async def refresh(refresh_token: str) -> Response[TokenResponse]:
    """
    刷新访问令牌
    
    Args:
        refresh_token: 刷新令牌
        
    Returns:
        Response[TokenResponse]: 标准响应格式的新令牌信息
        
    Raises:
        HTTPException: 刷新失败时抛出异常
    """
    try:
        token = await refresh_access_token(refresh_token)
        return Response(
            code=200,
            message="令牌刷新成功",
            data=token,
            request_id=str(uuid.uuid4()),
            timestamp=int(time.time() * 1000)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": AuthErrorCode.INVALID_TOKEN,
                "message": AuthErrorCode.get_message(AuthErrorCode.INVALID_TOKEN)
            }
        )

@router.get("/me", response_model=Response[UserOut])
async def get_user_info(current_user: UserOut = Depends(get_current_user)) -> Response[UserOut]:
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户依赖
        
    Returns:
        Response[UserOut]: 标准响应格式的用户信息
    """
    return Response(
        code=200,
        message="获取用户信息成功",
        data=current_user,
        request_id=str(uuid.uuid4()),
        timestamp=int(time.time() * 1000)
    ) 