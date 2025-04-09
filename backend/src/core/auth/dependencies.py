"""
认证依赖模块
"""
from typing import Annotated, Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from core.config import settings
from core.database import get_db
from core.database.redis import get_redis
from core.auth.models import User
from core.auth.schemas import TokenData, UserOut, TokenResponse
from core.auth.jwt import verify_token

# 避免循环导入
# from api.services.user import UserService

# 创建OAuth2密码承载器
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis)]
) -> User:
    """
    获取当前用户
    
    Args:
        token: JWT令牌
        db: 数据库会话
        redis: Redis客户端
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 认证失败时抛出异常
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 验证令牌
        payload = await verify_token(token, redis)
        
        # 获取用户ID
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
        
        # 查询用户 - 直接从数据库查询，避免使用UserService
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise credentials_exception
        
        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    except Exception:
        raise credentials_exception

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 当前活跃用户对象
        
    Raises:
        HTTPException: 用户不活跃时抛出异常
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    return current_user

async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    获取当前超级用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 当前超级用户对象
        
    Raises:
        HTTPException: 用户不是超级用户时抛出异常
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级用户权限"
        )
    return current_user

async def check_permissions(
    required_permissions: List[str],
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> bool:
    """
    检查用户权限
    
    Args:
        required_permissions: 所需权限列表
        current_user: 当前用户信息
        db: 数据库会话
        
    Returns:
        bool: 是否具有所需权限
        
    Raises:
        HTTPException: 权限不足时抛出异常
    """
    # 超级管理员拥有所有权限
    if current_user.is_superuser:
        return True
        
    # 获取用户权限 - 直接从数据库查询，避免使用UserService
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 从用户角色中获取权限
    user_permissions = []
    for role in user.roles:
        user_permissions.extend(role.permissions)
    
    # 检查是否具有所需权限
    if not all(perm in user_permissions for perm in required_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return True

async def refresh_access_token(
    refresh_token: str,
    redis: Annotated[Redis, Depends(get_redis)]
) -> TokenResponse:
    """
    刷新访问令牌
    
    Args:
        refresh_token: 刷新令牌
        redis: Redis客户端
        
    Returns:
        TokenResponse: 新的令牌信息
        
    Raises:
        HTTPException: 刷新令牌无效时抛出异常
    """
    try:
        payload = await verify_token(refresh_token, redis)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证信息",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        from .jwt import create_access_token, create_refresh_token
        
        # 创建新的令牌
        new_access_token = await create_access_token({"sub": user_id})
        new_refresh_token = await create_refresh_token({"sub": user_id})
        
        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=new_refresh_token
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"刷新令牌失败: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        ) 