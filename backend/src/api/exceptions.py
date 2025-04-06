from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Any, Dict, Optional

class APIException(Exception):
    """API异常基类"""
    def __init__(
        self,
        code: int = status.HTTP_400_BAD_REQUEST,
        message: str = "Bad Request",
        detail: Optional[Any] = None
    ):
        self.code = code
        self.message = message
        self.detail = detail

class NotFoundError(APIException):
    """资源未找到异常"""
    def __init__(self, message: str = "Resource not found", detail: Optional[Any] = None):
        super().__init__(
            code=status.HTTP_404_NOT_FOUND,
            message=message,
            detail=detail
        )

class ValidationError(APIException):
    """数据验证异常"""
    def __init__(self, message: str = "Validation error", detail: Optional[Any] = None):
        super().__init__(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            detail=detail
        )

class AuthenticationError(APIException):
    """认证异常"""
    def __init__(self, message: str = "Authentication failed", detail: Optional[Any] = None):
        super().__init__(
            code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            detail=detail
        )

class AuthorizationError(APIException):
    """授权异常"""
    def __init__(self, message: str = "Permission denied", detail: Optional[Any] = None):
        super().__init__(
            code=status.HTTP_403_FORBIDDEN,
            message=message,
            detail=detail
        )

async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """API异常处理器"""
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "message": exc.message,
            "detail": exc.detail,
            "path": request.url.path
        }
    )

async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """请求参数验证异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Validation error",
            "detail": exc.errors(),
            "path": request.url.path
        }
    ) 