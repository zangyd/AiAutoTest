"""
认证相关的常量定义
"""
from enum import Enum
from typing import Dict, Any

class AuthErrorCode(str, Enum):
    """认证错误码"""
    
    INVALID_CREDENTIALS = "AUTH_001"
    INVALID_TOKEN = "AUTH_002"
    USER_NOT_FOUND = "AUTH_003"
    USER_INACTIVE = "AUTH_004"
    INVALID_CAPTCHA = "AUTH_005"
    USER_LOCKED = "AUTH_006"
    PASSWORD_EXPIRED = "AUTH_007"
    TOKEN_EXPIRED = "AUTH_008"
    TOKEN_BLACKLISTED = "AUTH_009"
    
    @property
    def code(self) -> str:
        """获取错误码"""
        return self.value
        
    @property
    def message(self) -> str:
        """获取错误信息"""
        return ERROR_MESSAGES[self.value]
        
ERROR_MESSAGES: Dict[str, str] = {
    AuthErrorCode.INVALID_CREDENTIALS.value: "用户名或密码错误",
    AuthErrorCode.INVALID_TOKEN.value: "无效的访问令牌",
    AuthErrorCode.USER_NOT_FOUND.value: "用户不存在",
    AuthErrorCode.USER_INACTIVE.value: "用户已被禁用",
    AuthErrorCode.INVALID_CAPTCHA.value: "验证码错误",
    AuthErrorCode.USER_LOCKED.value: "账号已被锁定",
    AuthErrorCode.PASSWORD_EXPIRED.value: "密码已过期",
    AuthErrorCode.TOKEN_EXPIRED.value: "访问令牌已过期",
    AuthErrorCode.TOKEN_BLACKLISTED.value: "访问令牌已被禁用"
}

# 登录相关配置
LOGIN_CONFIG: Dict[str, Any] = {
    "max_attempts": 5,  # 最大尝试次数
    "lock_duration": 30,  # 锁定时长(分钟)
    "password_expire_days": 90,  # 密码过期天数
    "captcha_expire_minutes": 5,  # 验证码过期时间(分钟)
}

# Token相关配置
TOKEN_CONFIG: Dict[str, Any] = {
    "access_token_expire_minutes": 30,  # 访问令牌过期时间(分钟)
    "refresh_token_expire_days": 7,  # 刷新令牌过期时间(天)
    "token_type": "bearer",  # 令牌类型
    "algorithm": "HS256",  # 加密算法
} 