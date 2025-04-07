"""
认证依赖模块
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from core.config import settings
from core.database import get_db
from core.auth.models import User
from core.auth.schemas import TokenData
from api.services.user import UserService
from core.security import verify_token
from .schemas import UserOut, TokenResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    # 检查用户状态
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用"
        )
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前超级用户
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
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