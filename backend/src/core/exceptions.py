"""
自定义异常模块
"""
from fastapi import HTTPException, status

class InvalidCredentialsException(HTTPException):
    """无效的凭证异常"""
    def __init__(self, detail: str = "无效的用户名或密码"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class TokenBlacklistedException(HTTPException):
    """令牌已被加入黑名单异常"""
    def __init__(self, detail: str = "令牌已被撤销"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class CaptchaException(HTTPException):
    """验证码相关异常"""
    def __init__(self, detail: str = "验证码错误或已过期"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class AccountLockedException(HTTPException):
    """账户锁定异常"""
    def __init__(self, detail: str = "账户已被锁定"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class DatabaseError(HTTPException):
    """数据库操作异常"""
    def __init__(self, detail: str = "数据库操作失败"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class RedisError(HTTPException):
    """Redis操作异常"""
    def __init__(self, detail: str = "Redis操作失败"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        ) 