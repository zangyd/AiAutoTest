"""
API模型定义
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, constr
from enum import Enum
from .base import StatusEnum, DateTimeModelMixin

class PermissionEnum(str, Enum):
    """权限枚举"""
    # 用户管理权限
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # 角色管理权限
    ROLE_CREATE = "role:create"
    ROLE_READ = "role:read"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"
    
    # 系统管理权限
    SYSTEM_CONFIG = "system:config"
    SYSTEM_BACKUP = "system:backup"
    SYSTEM_RESTORE = "system:restore"
    
    # 数据管理权限
    DATA_IMPORT = "data:import"
    DATA_EXPORT = "data:export"
    DATA_DELETE = "data:delete"

class Permission(BaseModel):
    """权限模型"""
    code: PermissionEnum = Field(..., description="权限代码")
    name: str = Field(..., description="权限名称")
    description: Optional[str] = Field(None, description="权限描述")

class Role(BaseModel):
    """角色模型"""
    name: str = Field(..., description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    permissions: List[PermissionEnum] = Field(default=[], description="角色拥有的权限列表")

class RoleCreate(Role):
    """角色创建模型"""
    pass

class RoleUpdate(BaseModel):
    """角色更新模型"""
    name: Optional[str] = Field(None, description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    permissions: Optional[List[PermissionEnum]] = Field(None, description="角色拥有的权限列表")

class RoleOut(Role, DateTimeModelMixin):
    """角色输出模型"""
    id: int = Field(..., description="角色ID")

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    """用户基础模型"""
    username: constr(min_length=3, max_length=20) = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    department: str = Field(..., description="部门")
    position: str = Field(..., description="职位")
    status: StatusEnum = StatusEnum.ACTIVE
    roles: List[int] = Field(default=[], description="用户角色ID列表")
    permissions: List[PermissionEnum] = Field(default=[], description="用户权限列表")

class UserCreate(UserBase):
    """用户创建模型"""
    password: constr(min_length=8, max_length=20) = Field(..., description="密码")

class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    department: Optional[str] = Field(None, description="部门")
    position: Optional[str] = Field(None, description="职位")
    status: Optional[StatusEnum] = Field(None, description="状态")
    roles: Optional[List[int]] = Field(None, description="用户角色ID列表")
    permissions: Optional[List[PermissionEnum]] = Field(None, description="用户权限列表")
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