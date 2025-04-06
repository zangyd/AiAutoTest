from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from fastapi import Query
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 分页查询参数模型
class PaginationParams(BaseModel):
    page: int = Query(1, ge=1, description="页码")
    size: int = Query(10, ge=1, le=100, description="每页数量")
    
    @property
    def skip(self) -> int:
        return (self.page - 1) * self.size
        
    @property
    def limit(self) -> int:
        return self.size

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt

def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_REFRESH_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt 