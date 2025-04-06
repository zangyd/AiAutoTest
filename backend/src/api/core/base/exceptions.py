"""
基础异常类定义
"""
from fastapi import status
from typing import Any, Optional

class BaseAPIException(Exception):
    """API异常基类"""
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: int = 40000,
        message: str = "Bad Request",
        details: Optional[Any] = None
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details

class NotFoundError(BaseAPIException):
    """资源未找到异常"""
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code=40401,
            message=f"{resource} with id {resource_id} not found",
            details={"resource": resource, "id": resource_id}
        )

class ValidationError(BaseAPIException):
    """数据验证异常"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=42201,
            message=message,
            details=details
        )

class DatabaseError(BaseAPIException):
    """数据库操作异常"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=50001,
            message=message,
            details=details
        )

class ConfigurationError(BaseAPIException):
    """配置错误异常"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=50002,
            message=message,
            details=details
        ) 