"""
认证相关的请求/响应模型
"""
from pydantic import BaseModel, Field
from backend.src.core.auth.schemas import TokenResponse, UserOut

class CaptchaResponse(BaseModel):
    """验证码响应模型"""
    captcha_id: str = Field(..., description="验证码ID")
    image: str = Field(..., description="Base64编码的验证码图片")

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    captcha_id: str = Field(..., description="验证码ID")
    captcha_code: str = Field(..., description="验证码")
    remember: bool = Field(default=False, description="是否记住登录状态")

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str = Field(..., description="刷新令牌") 