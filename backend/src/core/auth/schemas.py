"""
认证模块的核心模型
"""
from pydantic import BaseModel, Field, EmailStr, constr, conint
from typing import Optional

class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: constr(pattern="^bearer$") = Field(..., description="令牌类型")
    expires_in: conint(gt=0) = Field(..., description="过期时间(秒)")
    refresh_token: str = Field(..., description="刷新令牌")

class UserOut(BaseModel):
    """用户信息响应模型"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    is_active: bool = Field(..., description="是否激活")
    is_superuser: bool = Field(..., description="是否超级用户") 