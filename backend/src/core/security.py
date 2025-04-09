"""
安全相关的工具函数
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from core.config import settings
from .config.jwt_config import jwt_settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    获取密码哈希值
    
    Args:
        password: 原始密码
        
    Returns:
        str: 密码哈希值
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 原始密码
        hashed_password: 密码哈希值
        
    Returns:
        bool: 密码是否正确
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_tokens(data: dict) -> Tuple[str, str]:
    """
    创建访问令牌和刷新令牌
    
    Args:
        data: 要编码到令牌中的数据
        
    Returns:
        Tuple[str, str]: (访问令牌, 刷新令牌)
    """
    # 创建访问令牌
    access_token_data = data.copy()
    access_token_data.update({
        "exp": datetime.utcnow() + jwt_settings.access_token_expires,
        "token_type": "access"
    })
    access_token = jwt.encode(
        access_token_data,
        jwt_settings.JWT_SECRET_KEY,
        algorithm=jwt_settings.JWT_ALGORITHM
    )
    
    # 创建刷新令牌
    refresh_token_data = data.copy()
    refresh_token_data.update({
        "exp": datetime.utcnow() + jwt_settings.refresh_token_expires,
        "token_type": "refresh"
    })
    refresh_token = jwt.encode(
        refresh_token_data,
        jwt_settings.JWT_SECRET_KEY,
        algorithm=jwt_settings.JWT_ALGORITHM
    )
    
    return access_token, refresh_token

def verify_token(token: str, token_type: str = "access") -> Union[dict, None]:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌字符串
        token_type: 令牌类型("access" 或 "refresh")
        
    Returns:
        Union[dict, None]: 如果令牌有效，返回解码后的数据；否则返回None
    """
    try:
        payload = jwt.decode(
            token,
            jwt_settings.JWT_SECRET_KEY,
            algorithms=[jwt_settings.JWT_ALGORITHM]
        )
        
        # 验证令牌类型
        if payload.get("token_type") != token_type:
            return None
            
        return payload
    except JWTError:
        return None

def refresh_access_token(refresh_token: str) -> Union[str, None]:
    """
    使用刷新令牌生成新的访问令牌
    
    Args:
        refresh_token: 刷新令牌
        
    Returns:
        Union[str, None]: 如果刷新令牌有效，返回新的访问令牌；否则返回None
    """
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        return None
        
    # 移除令牌类型和过期时间
    del payload["token_type"]
    del payload["exp"]
    
    # 创建新的访问令牌
    access_token_data = payload.copy()
    access_token_data.update({
        "exp": datetime.utcnow() + jwt_settings.access_token_expires,
        "token_type": "access"
    })
    
    return jwt.encode(
        access_token_data,
        jwt_settings.JWT_SECRET_KEY,
        algorithm=jwt_settings.JWT_ALGORITHM
    ) 