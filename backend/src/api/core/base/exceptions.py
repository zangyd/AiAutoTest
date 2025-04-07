"""
异常定义模块

定义API使用的自定义异常类
"""
from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class APIException(HTTPException):
    """API基础异常类"""
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ValidationError(APIException):
    """数据验证错误"""
    def __init__(self, detail: Any = "Invalid input") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class NotFoundError(APIException):
    """资源未找到错误"""
    def __init__(self, detail: Any = "Resource not found") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class AuthenticationError(APIException):
    """认证错误"""
    def __init__(self, detail: Any = "Authentication failed") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class PermissionError(APIException):
    """权限错误"""
    def __init__(self, detail: Any = "Permission denied") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class BusinessError(APIException):
    """业务逻辑错误"""
    def __init__(self, detail: Any = "Business logic error") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class DatabaseError(APIException):
    """数据库操作异常"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )

class ConfigurationError(APIException):
    """配置错误异常"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        ) 