"""
认证模块数据模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
import re

class TokenData(BaseModel):
    """
    令牌数据模型
    """
    username: str
    exp: Optional[datetime] = None

class UserBase(BaseModel):
    """
    用户基础模型
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone: Optional[str] = None

    @validator('phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('无效的手机号格式')
        return v

class UserCreate(UserBase):
    """
    用户创建模型
    """
    password: str = Field(..., min_length=8, max_length=32)

    @validator('password')
    def validate_password(cls, v):
        """验证密码强度"""
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', v):
            raise ValueError('密码必须包含大小写字母、数字和特殊字符')
        return v

class UserUpdate(BaseModel):
    """
    用户更新模型
    """
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('无效的手机号格式')
        return v

    @validator('password')
    def validate_password(cls, v):
        """验证密码强度"""
        if v and not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', v):
            raise ValueError('密码必须包含大小写字母、数字和特殊字符')
        return v

class UserLogin(BaseModel):
    """
    用户登录模型
    """
    username: str
    password: str
    remember: Optional[bool] = False
    captcha: Optional[str] = None
    captcha_id: Optional[str] = None

class UserOut(BaseModel):
    """
    用户输出模型
    """
    id: int
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        """配置"""
        orm_mode = True

class TokenResponse(BaseModel):
    """
    令牌响应模型
    """
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    refresh_token: str = Field(..., description="刷新令牌")

class RefreshToken(BaseModel):
    """
    刷新令牌模型
    """
    refresh_token: str

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str = Field(..., description="刷新令牌")

class LogoutRequest(BaseModel):
    """登出请求模型"""
    token: str = Field(..., description="要撤销的访问令牌")
    refresh_token: Optional[str] = Field(None, description="要撤销的刷新令牌")

class RoleBase(BaseModel):
    """
    角色基础模型
    """
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None

class RoleCreate(RoleBase):
    """
    角色创建模型
    """
    pass

class RoleUpdate(RoleBase):
    """
    角色更新模型
    """
    pass

class RoleOut(RoleBase):
    """
    角色输出模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """配置"""
        from_attributes = True

class UserRoleCreate(BaseModel):
    """
    用户角色关联创建模型
    """
    user_id: int
    role_id: int

class UserRoleOut(BaseModel):
    """
    用户角色关联输出模型
    """
    user_id: int
    role_id: int
    created_at: datetime

    class Config:
        """配置"""
        from_attributes = True

# ... 其他模型 ... 