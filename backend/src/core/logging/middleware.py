"""
日志中间件模块

提供请求响应日志记录功能
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    """日志记录中间件"""
    
    def __init__(self, app: ASGIApp):
        """
        初始化中间件
        
        Args:
            app: ASGI应用实例
        """
        super().__init__(app)
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        处理请求并记录日志
        
        Args:
            request: 请求对象
            call_next: 下一个处理函数
            
        Returns:
            Response: 响应对象
        """
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        request_id = request.headers.get("X-Request-ID", "")
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else ""
        user_agent = request.headers.get("User-Agent", "")
        
        # 记录请求日志
        logger.info(
            "收到API请求",
            request_id=request_id,
            method=method,
            url=url,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应日志
            logger.info(
                "请求处理完成",
                request_id=request_id,
                method=method,
                url=url,
                status_code=response.status_code,
                process_time=f"{process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            # 记录错误日志
            process_time = time.time() - start_time
            logger.error(
                "请求处理异常",
                request_id=request_id,
                method=method,
                url=url,
                error=str(e),
                process_time=f"{process_time:.3f}s"
            )
            raise 