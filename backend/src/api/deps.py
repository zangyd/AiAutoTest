from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from tests.config import JWT_CONFIG, TEST_USERS

from .models import UserOut
from .base import StatusEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_CONFIG["access_token_expire_minutes"])
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        JWT_CONFIG["secret_key"], 
        algorithm=JWT_CONFIG["algorithm"]
    )
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            JWT_CONFIG["secret_key"], 
            algorithms=[JWT_CONFIG["algorithm"]]
        )
        token_type = payload.get("type")
        if token_type == "admin_token":
            return TEST_USERS["admin"]
        elif token_type == "user_token":
            return TEST_USERS["user"]
        else:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

def check_permissions(user: dict, required_permissions: List[str]) -> bool:
    """检查用户权限"""
    if not user.get("permissions"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限"
        )
    
    if not all(perm in user["permissions"] for perm in required_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return True

def require_permissions(permissions: List[str]):
    """权限要求装饰器"""
    def decorator(func):
        async def wrapper(*args, current_user: dict = Depends(get_current_user), **kwargs):
            check_permissions(current_user, permissions)
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

async def check_permissions(user: UserOut, required_permissions: List[str]) -> None:
    """检查用户权限"""
    if not user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permissions"
        )
    
    # 检查是否具有所需权限
    if not all(perm in user.permissions for perm in required_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

def require_permissions(*permissions: str):
    """权限要求装饰器"""
    async def check_user_permissions(user: UserOut = Depends(get_current_user)):
        await check_permissions(user, list(permissions))
        return user
    return Depends(check_user_permissions) 