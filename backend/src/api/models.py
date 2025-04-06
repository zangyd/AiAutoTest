"""
API模型定义
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, constr
from .base import StatusEnum, DateTimeModelMixin

class UserBase(BaseModel):
    """用户基础模型"""
    username: constr(min_length=3, max_length=20) = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    department: str = Field(..., description="部门")
    position: str = Field(..., description="职位")
    status: StatusEnum = StatusEnum.ACTIVE
    permissions: List[str] = []

class UserCreate(UserBase):
    """用户创建模型"""
    password: constr(min_length=8, max_length=20) = Field(..., description="密码")

class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    department: Optional[str] = Field(None, description="部门")
    position: Optional[str] = Field(None, description="职位")
    status: Optional[StatusEnum] = Field(None, description="状态")
    permissions: Optional[List[str]] = Field(None, description="用户权限列表")
    password: Optional[constr(min_length=8, max_length=20)] = Field(None, description="密码")

class UserOut(UserBase, DateTimeModelMixin):
    """用户输出模型"""
    id: int = Field(..., description="用户ID")

    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str 