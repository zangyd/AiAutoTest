"""
认证模块常量定义
"""

class AuthErrorCode:
    INVALID_CAPTCHA = "AUTH_001"
    INVALID_CREDENTIALS = "AUTH_002"
    INVALID_TOKEN = "AUTH_003"
    GENERATE_CAPTCHA_FAILED = "AUTH_004"
    
    @staticmethod
    def get_message(code: str) -> str:
        messages = {
            "AUTH_001": "验证码错误或已过期",
            "AUTH_002": "用户名或密码错误",
            "AUTH_003": "无效的令牌或已过期",
            "AUTH_004": "验证码生成失败"
        }
        return messages.get(code, "未知错误") 