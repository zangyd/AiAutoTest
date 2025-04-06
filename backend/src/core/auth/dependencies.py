"""
认证依赖模块
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .jwt import verify_token
from .schemas import UserOut, TokenResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserOut:
    """
    获取当前用户
    
    Args:
        token: JWT令牌
        
    Returns:
        UserOut: 当前用户信息
        
    Raises:
        HTTPException: 认证失败时抛出异常
    """
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证信息",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # 这里应该从数据库获取用户信息
        # 目前使用模拟数据
        if user_id == "1":
            return UserOut(
                id=1,
                username="test_user",
                email="test@example.com",
                is_active=True,
                is_superuser=False
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
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