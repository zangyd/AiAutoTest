"""
认证相关API接口
"""
from fastapi import APIRouter, Depends, Body, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from redis.asyncio import Redis
from typing import Annotated, Optional

from core.database import get_db
from core.database.redis import get_redis
from core.auth.service import AuthService
from core.auth.schemas import TokenResponse, RefreshToken, UserLogin, UserOut, RefreshTokenRequest, LogoutRequest, CaptchaResponse
from core.auth.models import User
from core.auth.jwt import create_access_token, create_refresh_token, verify_token
from core.auth.dependencies import get_current_user
from core.auth.token_blacklist import TokenBlacklist
from core.auth.captcha import CaptchaManager
from core.auth.login_log import LoginLogService
from core.cache.redis_manager import get_redis_client

router = APIRouter(prefix="/auth", tags=["认证"])

# 创建OAuth2密码承载器
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 在需要时导入Redis依赖
def get_redis_dependency():
    """获取Redis依赖，延迟导入"""
    from core.database.redis import get_redis
    return get_redis

# 在router中直接实现get_current_user依赖项，避免循环导入
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    获取当前用户
    
    Args:
        token: JWT令牌
        db: 数据库会话
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 令牌无效或用户不存在时抛出异常
    """
    try:
        # 解码令牌
        payload = verify_token(token)
        
        # 获取用户ID
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证信息",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 查询用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已被禁用"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"认证失败: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post("/captcha", response_model=CaptchaResponse)
async def generate_captcha(
    request: Request,
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis_client)
):
    """
    生成图形验证码
    
    返回验证码ID和图像的Base64编码
    """
    captcha_manager = CaptchaManager(redis_client)
    auth_service = AuthService(db=db, redis=redis_client, captcha_manager=captcha_manager)
    
    return await auth_service.generate_captcha()

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    user_login: UserLogin,
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis_client)
):
    """
    用户登录接口
    """
    # 获取客户端信息用于日志记录
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # 创建认证服务和验证码管理器
    captcha_manager = CaptchaManager(redis_client)
    token_blacklist = TokenBlacklist(redis_client)
    auth_service = AuthService(
        db=db, 
        redis=redis_client, 
        token_blacklist=token_blacklist,
        captcha_manager=captcha_manager
    )
    
    # 验证用户凭据
    user = await auth_service.authenticate_user(
        username=user_login.username,
        password=user_login.password,
        captcha_id=user_login.captcha_id,
        captcha_text=user_login.captcha_text,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # 创建令牌
    access_token, refresh_token = await auth_service.create_tokens(user.id, user.username)
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends()]
):
    """
    刷新访问令牌
    
    Args:
        request: 刷新令牌请求
        auth_service: 认证服务
        
    Returns:
        TokenResponse: 新的令牌信息
    """
    # 验证刷新令牌并获取新的访问令牌
    access_token = await auth_service.refresh_access_token(request.refresh_token)
    
    # 构建响应
    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # 刷新令牌不变
        token_type="Bearer",
        expires_in=60 * 30  # 30分钟
    )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: LogoutRequest,
    auth_service: Annotated[AuthService, Depends()],
    redis: Annotated[Redis, Depends(get_redis_dependency())]
):
    """
    用户登出
    
    Args:
        request: 登出请求
        auth_service: 认证服务
    """
    # 将令牌加入黑名单
    success = await auth_service.logout(request.token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="登出失败"
        )
    
    # 如果提供了刷新令牌，也将其加入黑名单
    if request.refresh_token:
        await auth_service.logout(request.refresh_token)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        UserOut: 用户信息
    """
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        phone=current_user.phone,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login=current_user.last_login
    )
