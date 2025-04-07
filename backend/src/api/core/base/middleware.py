"""
中间件模块

定义API使用的中间件
"""
import time
from typing import Callable, Dict, Optional
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
import json
from .utils import generate_request_id
from .config import settings
from .exceptions import APIException

# 配置日志
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    filename=settings.LOG_FILE
)
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = generate_request_id()
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        logger.info(
            f"Request started: {request_id} - {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else None,
            }
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"Request completed: {request_id} - {response.status_code} - {process_time:.3f}s",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": process_time,
                }
            )
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 记录错误信息
            logger.error(
                f"Request failed: {request_id} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                },
                exc_info=True
            )
            raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""
    def __init__(
        self,
        app: ASGIApp,
        calls: int = 100,
        period: int = 60
    ):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.cache: Dict[str, Dict] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 检查并更新速率限制
        current_time = time.time()
        if client_ip in self.cache:
            data = self.cache[client_ip]
            if current_time - data["start_time"] >= self.period:
                # 重置计数
                data["count"] = 1
                data["start_time"] = current_time
            else:
                # 增加计数
                data["count"] += 1
                if data["count"] > self.calls:
                    return Response(
                        content=json.dumps({
                            "detail": "Too many requests"
                        }),
                        status_code=429,
                        media_type="application/json"
                    )
        else:
            # 新的客户端
            self.cache[client_ip] = {
                "count": 1,
                "start_time": current_time
            }
        
        return await call_next(request)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except APIException as e:
            # API异常直接返回
            return Response(
                content=str(e.detail),
                status_code=e.status_code,
                headers=e.headers
            )
        except Exception as e:
            # 其他异常转换为500错误
            return Response(
                content=str(e),
                status_code=500
            )

def setup_middleware(app: FastAPI) -> None:
    """配置中间件"""
    # 跨域中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 可信主机中间件
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
    
    # 请求日志中间件
    app.add_middleware(RequestLoggingMiddleware)
    
    # 速率限制中间件
    app.add_middleware(
        RateLimitMiddleware,
        calls=100,  # 每分钟最大请求数
        period=60   # 时间窗口（秒）
    )
    
    # 错误处理中间件
    app.add_middleware(ErrorHandlingMiddleware)