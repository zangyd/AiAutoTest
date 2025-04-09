"""
基础模型定义
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, constr, ConfigDict
from core.auth.models import Role

class StatusEnum(str, Enum):
    """状态枚举"""
    ACTIVE = "active"      # 活动状态
    INACTIVE = "inactive"  # 非活动状态
    DELETED = "deleted"    # 已删除

class PriorityEnum(str, Enum):
    """优先级枚举"""
    P0 = "P0"  # 最高优先级
    P1 = "P1"  # 高优先级
    P2 = "P2"  # 中优先级
    P3 = "P3"  # 低优先级
    P4 = "P4"  # 最低优先级

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

class BaseTimeModel(BaseModel):
    """基础时间模型"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class Permission(BaseModel):
    """权限模型"""
    code: str
    name: str
    description: Optional[str] = None

class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: str
    real_name: str
    position: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    department: str = Field(..., description="部门")
    status: StatusEnum = StatusEnum.ACTIVE
    roles: List[int] = Field(default=[], description="用户角色ID列表")
    permissions: List[PermissionEnum] = Field(default=[], description="用户权限列表") 