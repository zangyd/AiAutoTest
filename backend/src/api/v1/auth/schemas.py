"""
认证相关的Pydantic模型
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class PermissionBase(BaseModel):
    """权限基础模型"""
    code: str = Field(..., max_length=100)
    name: str = Field(..., max_length=50)
    type: str = Field(..., max_length=50)
    resource: str = Field(..., max_length=200)
    action: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=200)

class PermissionCreate(PermissionBase):
    """创建权限的请求模型"""
    pass

class PermissionUpdate(PermissionBase):
    """更新权限的请求模型"""
    pass

class PermissionResponse(PermissionBase):
    """权限的响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoleBase(BaseModel):
    """角色基础模型"""
    name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    is_system: bool = False

class RoleCreate(RoleBase):
    """创建角色的请求模型"""
    pass

class RoleUpdate(RoleBase):
    """更新角色的请求模型"""
    pass

class RoleResponse(RoleBase):
    """角色的响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    permissions: List[PermissionResponse] = []

    model_config = ConfigDict(from_attributes=True)

class DepartmentBase(BaseModel):
    """部门基础模型"""
    name: str = Field(..., max_length=50)
    path: str = Field(..., max_length=500)
    description: Optional[str] = Field(None, max_length=200)
    parent_id: Optional[int] = None
    level: int = 1

class DepartmentCreate(DepartmentBase):
    """创建部门的请求模型"""
    pass

class DepartmentUpdate(DepartmentBase):
    """更新部门的请求模型"""
    pass

class DepartmentResponse(DepartmentBase):
    """部门的响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    children: List['DepartmentResponse'] = []

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=100)
    real_name: str = Field(..., max_length=50)
    position: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """创建用户的请求模型"""
    password: str = Field(..., min_length=6, max_length=50)
    role_ids: List[int] = []
    department_ids: List[int] = []

class UserUpdate(BaseModel):
    """更新用户的请求模型"""
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    real_name: Optional[str] = Field(None, max_length=50)
    position: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6, max_length=50)
    role_ids: Optional[List[int]] = None
    department_ids: Optional[List[int]] = None

class UserResponse(UserBase):
    """用户的响应模型"""
    id: int
    locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    login_attempts: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    roles: List[RoleResponse] = []
    departments: List[DepartmentResponse] = []

    model_config = ConfigDict(from_attributes=True)

class LoginLog(BaseModel):
    """登录日志模型"""
    id: int
    user_id: int
    ip_address: str
    user_agent: str
    status_message: str
    login_time: datetime
    login_status: bool
    captcha_verified: bool

    model_config = ConfigDict(from_attributes=True)

class OperationLog(BaseModel):
    """操作日志模型"""
    id: int
    user_id: int
    operation_type: str
    operation_content: str
    ip_address: str
    user_agent: str
    error_message: Optional[str] = None
    status: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str

class TokenData(BaseModel):
    """令牌数据模型"""
    username: str
    exp: datetime

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str
    captcha_id: str
    captcha_code: str

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    old_password: str = Field(..., min_length=6, max_length=50)
    new_password: str = Field(..., min_length=6, max_length=50)
    confirm_password: str = Field(..., min_length=6, max_length=50)

class ResetPasswordRequest(BaseModel):
    """重置密码请求模型"""
    email: EmailStr
    verification_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6, max_length=50)
    confirm_password: str = Field(..., min_length=6, max_length=50)

class SendVerificationCodeRequest(BaseModel):
    """发送验证码请求模型"""
    email: EmailStr

class CaptchaResponse(BaseModel):
    """验证码响应模型"""
    captcha_id: str
    captcha_image: str  # Base64编码的图片
