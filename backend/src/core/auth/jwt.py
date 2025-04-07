"""
JWT令牌处理模块
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from core.database import get_db
from core.config.settings import settings
from .models import User
from .token_blacklist import TokenBlacklist

# 创建OAuth2密码承载器
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 全局黑名单实例
_token_blacklist: Optional[TokenBlacklist] = None

def get_token_blacklist(redis: Redis) -> TokenBlacklist:
    """
    获取令牌黑名单实例
    
    Args:
        redis: Redis客户端
        
    Returns:
        TokenBlacklist: 令牌黑名单实例
    """
    global _token_blacklist
    if _token_blacklist is None:
        _token_blacklist = TokenBlacklist(redis)
    return _token_blacklist

async def create_access_token(data: Dict[str, Any]) -> str:
    """
    创建访问令牌
    
    Args:
        data: 令牌数据
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"无法创建访问令牌: {str(e)}"
        )

async def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    创建刷新令牌
    
    Args:
        data: 令牌数据
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "refresh": True})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"无法创建刷新令牌: {str(e)}"
        )

async def verify_token(token: str, redis: Optional[Redis] = None) -> Dict[str, Any]:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌
        redis: Redis客户端，用于检查黑名单
        
    Returns:
        Dict[str, Any]: 解码后的令牌数据
        
    Raises:
        HTTPException: 令牌验证失败
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 验证令牌是否有效
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # 检查令牌是否在黑名单中
        if redis:
            blacklist = get_token_blacklist(redis)
            if await blacklist.is_blacklisted(token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="令牌已被撤销",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception

async def revoke_token(token: str, redis: Redis) -> bool:
    """
    撤销令牌（加入黑名单）
    
    Args:
        token: JWT令牌
        redis: Redis客户端
        
    Returns:
        bool: 是否成功撤销
    """
    blacklist = get_token_blacklist(redis)
    return await blacklist.add_to_blacklist(token)

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