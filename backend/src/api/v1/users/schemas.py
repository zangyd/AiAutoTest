"""
用户相关的请求/响应模型
"""
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

from ....core.base.models import StatusEnum

class UserBase(BaseModel):
    """用户基础信息模型"""
    username: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    department: str = Field(..., description="部门")
    position: str = Field(..., description="职位")

class UserCreate(UserBase):
    """用户创建请求模型"""
    password: str = Field(..., description="密码")

class UserUpdate(BaseModel):
    """用户更新请求模型"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    department: Optional[str] = Field(None, description="部门")
    position: Optional[str] = Field(None, description="职位")
    status: Optional[StatusEnum] = Field(None, description="状态")
    permissions: Optional[List[str]] = Field(None, description="权限列表")

class UserOut(UserBase):
    """用户信息响应模型"""
    id: int = Field(..., description="用户ID")
    status: StatusEnum = Field(..., description="状态")
    permissions: List[str] = Field(default=[], description="权限列表") 