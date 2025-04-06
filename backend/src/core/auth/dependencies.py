"""
认证依赖模块
"""
from typing import Optional, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.src.core.database import get_db
from backend.src.api.services.user import UserService
from backend.src.core.security import verify_token
from .schemas import UserOut, TokenResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserOut:
    """
    获取当前用户
    
    Args:
        token: JWT令牌
        db: 数据库会话
        
    Returns:
        UserOut: 当前用户信息
        
    Raises:
        HTTPException: 认证失败时抛出异常
    """
    try:
        # 验证令牌
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证信息",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # 从数据库获取用户
        user_service = UserService(db)
        user = user_service.get_user_by_id(int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
            
        return UserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_superuser=user.is_superuser
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_active_user(
    current_user: UserOut = Depends(get_current_user)
) -> UserOut:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        UserOut: 当前活跃用户信息
        
    Raises:
        HTTPException: 用户未激活时抛出异常
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
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
        
    # 获取用户权限
    user_service = UserService(db)
    user = user_service.get_user_by_id(current_user.id)
    user_permissions = user_service.get_user_permissions(user)
    
    # 检查是否具有所需权限
    if not all(perm in user_permissions for perm in required_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return True

async def refresh_access_token(refresh_token: str) -> TokenResponse:
    """
    刷新访问令牌
    
    Args:
        refresh_token: 刷新令牌
        
    Returns:
        TokenResponse: 新的令牌信息
        
    Raises:
        HTTPException: 刷新令牌无效时抛出异常
    """
    try:
        payload = verify_token(refresh_token)
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
        new_access_token = create_access_token({"sub": user_id})
        new_refresh_token = create_refresh_token({"sub": user_id})
        
        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=3600,
            refresh_token=new_refresh_token
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        ) 