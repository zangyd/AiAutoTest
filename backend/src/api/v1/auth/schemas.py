"""
认证相关的请求/响应模型
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field
from backend.src.core.auth.schemas import TokenResponse, UserOut

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    """标准响应格式"""
    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    request_id: Optional[str] = Field(None, description="请求追踪ID")
    timestamp: Optional[int] = Field(None, description="时间戳")

class PaginationParams(BaseModel):
    """分页查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页大小")

class CaptchaResponse(BaseModel):
    """验证码响应模型"""
    captcha_id: str = Field(..., description="验证码ID")
    image: str = Field(..., description="Base64编码的验证码图片")

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., min_length=8, max_length=20, description="密码")
    captcha_id: str = Field(..., description="验证码ID")
    captcha_code: str = Field(..., min_length=4, max_length=4, description="验证码")
    remember: bool = Field(default=False, description="是否记住登录状态")

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str = Field(..., description="刷新令牌") 