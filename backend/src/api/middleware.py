import time
import uuid
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging

# 配置日志
logger = logging.getLogger("api")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s"
                }
            )
            
            # 在响应头中添加请求ID
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # 记录异常信息
            logger.error(
                f"Request failed",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time": f"{time.time() - start_time:.3f}s"
                },
                exc_info=True
            )
            raise

def setup_middleware(app):
    """设置中间件"""
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 在生产环境中应该限制允许的源
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加请求日志中间件
    app.add_middleware(RequestLoggingMiddleware) 