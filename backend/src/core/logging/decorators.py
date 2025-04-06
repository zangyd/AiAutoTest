"""
日志装饰器模块

提供方法调用和数据变更的日志记录功能
"""
import time
import functools
from typing import Any, Callable, Dict, Optional, Type
from fastapi import Request
from pydantic import BaseModel

from .logger import logger

def log_method_call(method_name: Optional[str] = None):
    """
    方法调用日志装饰器
    
    Args:
        method_name: 方法名称，如果不提供则使用函数名
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取方法名
            name = method_name or func.__name__
            
            # 记录调用开始
            start_time = time.time()
            logger.info(
                f"开始调用方法: {name}",
                method=name,
                args=str(args),
                kwargs=str(kwargs)
            )
            
            try:
                # 执行方法
                result = await func(*args, **kwargs)
                
                # 计算执行时间
                execution_time = time.time() - start_time
                
                # 记录调用成功
                logger.info(
                    f"方法调用成功: {name}",
                    method=name,
                    execution_time=f"{execution_time:.3f}s"
                )
                
                return result
                
            except Exception as e:
                # 记录调用失败
                execution_time = time.time() - start_time
                logger.error(
                    f"方法调用失败: {name}",
                    method=name,
                    error=str(e),
                    execution_time=f"{execution_time:.3f}s"
                )
                raise
                
        return wrapper
    return decorator

def log_data_change(model: Type[BaseModel], operation: str):
    """
    数据变更日志装饰器
    
    Args:
        model: Pydantic模型类
        operation: 操作类型（create/update/delete）
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取请求和用户信息
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            user_id = getattr(request.state, "user_id", None) if request else None
            
            try:
                # 执行操作
                result = await func(*args, **kwargs)
                
                # 记录数据变更
                log_data = {
                    "model": model.__name__,
                    "operation": operation,
                    "user_id": user_id
                }
                
                # 根据操作类型记录不同的数据
                if operation == "create":
                    log_data["new_data"] = result.dict() if isinstance(result, BaseModel) else str(result)
                elif operation == "update":
                    log_data["updated_data"] = result.dict() if isinstance(result, BaseModel) else str(result)
                elif operation == "delete":
                    log_data["deleted_id"] = kwargs.get("id") or getattr(result, "id", None)
                
                logger.info(
                    f"数据{operation}操作成功",
                    **log_data
                )
                
                return result
                
            except Exception as e:
                # 记录操作失败
                logger.error(
                    f"数据{operation}操作失败",
                    model=model.__name__,
                    operation=operation,
                    error=str(e),
                    user_id=user_id
                )
                raise
                
        return wrapper
    return decorator 