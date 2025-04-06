from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, constr
from .base import StatusEnum, DateTimeModelMixin

class UserBase(BaseModel):
    """用户基础模型"""
    username: constr(min_length=3, max_length=20) = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    department: str = Field(..., description="部门")
    position: str = Field(..., description="职位")

class UserCreate(UserBase):
    """用户创建模型"""
    password: constr(min_length=8, max_length=20) = Field(..., description="密码")

class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    department: Optional[str] = Field(None, description="部门")
    position: Optional[str] = Field(None, description="职位")
    status: Optional[StatusEnum] = Field(None, description="状态")

class UserOut(UserBase, DateTimeModelMixin):
    """用户输出模型"""
    id: int = Field(..., description="用户ID")
    status: StatusEnum = Field(default=StatusEnum.ACTIVE, description="状态")
    permissions: Optional[List[str]] = Field(default=None, description="用户权限列表")

    class Config:
        orm_mode = True 