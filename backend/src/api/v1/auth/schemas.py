"""
认证相关的请求响应模型
"""
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel, Field, constr

from core.auth.schemas import TokenResponse, UserOut

# 定义泛型类型变量
T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    """标准响应模型"""
    code: int = Field(..., description="状态码")
    message: str = Field(..., description="消息")
    data: Optional[T] = Field(None, description="数据")


class PaginationParams(BaseModel):
    """分页查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页大小")

class CaptchaResponse(BaseModel):
    """验证码响应模型"""
    captcha_id: str = Field(..., description="验证码ID")
    image: str = Field(..., description="验证码图片(base64)")

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: constr(min_length=3, max_length=50) = Field(..., description="用户名")
    password: constr(min_length=6, max_length=50) = Field(..., description="密码")
    captcha_id: str = Field(..., description="验证码ID")
    captcha_code: constr(min_length=4, max_length=4) = Field(..., description="验证码")
    remember: bool = Field(False, description="记住登录状态")

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str = Field(..., description="刷新令牌") 