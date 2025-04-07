"""认证工具模块"""
import bcrypt
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import jwt

from core.config import settings


def get_password_hash(password: str) -> str:
    """
    获取密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        str: 密码哈希
    """
    # 生成盐值
    salt = bcrypt.gensalt()
    # 哈希密码
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 密码是否匹配
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        # 如果发生异常（比如哈希密码格式不正确），返回False
        return False 