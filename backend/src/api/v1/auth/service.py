"""
认证相关的业务逻辑
"""
import uuid
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .schemas import CaptchaResponse, TokenResponse
from backend.src.core.utils.captcha import CaptchaGenerator
from backend.src.core.cache.captcha import CaptchaCache
from backend.src.core.auth.dependencies import refresh_access_token
from backend.src.core.auth.service import auth_service
from .constants import AuthErrorCode

# 初始化验证码生成器和缓存
captcha_generator = CaptchaGenerator()
captcha_cache = CaptchaCache()

async def generate_captcha() -> CaptchaResponse:
    """
    生成验证码
    
    Returns:
        CaptchaResponse: 验证码信息
        
    Raises:
        HTTPException: 验证码生成失败时抛出异常
    """
    try:
        # 生成验证码ID
        captcha_id = str(uuid.uuid4())
        
        # 生成验证码
        code, image = captcha_generator.generate()
        
        # 保存验证码
        if not captcha_cache.save_captcha(captcha_id, code):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": AuthErrorCode.GENERATE_CAPTCHA_FAILED,
                    "message": AuthErrorCode.get_message(AuthErrorCode.GENERATE_CAPTCHA_FAILED)
                }
            )
        
        return CaptchaResponse(
            captcha_id=captcha_id,
            image=image
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": AuthErrorCode.GENERATE_CAPTCHA_FAILED,
                "message": AuthErrorCode.get_message(AuthErrorCode.GENERATE_CAPTCHA_FAILED)
            }
        )

async def verify_login(username: str, password: str, captcha_id: str, captcha_code: str, remember: bool) -> TokenResponse:
    """
    验证登录信息
    
    Args:
        username: 用户名
        password: 密码
        captcha_id: 验证码ID
        captcha_code: 验证码
        remember: 是否记住登录状态
        
    Returns:
        TokenResponse: 令牌信息
        
    Raises:
        HTTPException: 登录失败时抛出异常
    """
    # 验证验证码
    if not captcha_cache.verify_captcha(captcha_id, captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": AuthErrorCode.INVALID_CAPTCHA,
                "message": AuthErrorCode.get_message(AuthErrorCode.INVALID_CAPTCHA)
            }
        )
    
    try:
        # 使用核心认证服务进行认证
        user = await auth_service.authenticate_user(username, password)
        token = await auth_service.create_access_token(user, remember)
        return token
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": AuthErrorCode.INVALID_CREDENTIALS,
                "message": AuthErrorCode.get_message(AuthErrorCode.INVALID_CREDENTIALS)
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

async def refresh_token(refresh_token: str) -> TokenResponse:
    """
    刷新访问令牌
    
    Args:
        refresh_token: 刷新令牌
        
    Returns:
        TokenResponse: 新的令牌信息
        
    Raises:
        HTTPException: 刷新失败时抛出异常
    """
    try:
        return await refresh_access_token(refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": AuthErrorCode.INVALID_TOKEN,
                "message": AuthErrorCode.get_message(AuthErrorCode.INVALID_TOKEN)
            },
            headers={"WWW-Authenticate": "Bearer"}
        ) 