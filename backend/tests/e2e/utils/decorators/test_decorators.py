"""
测试装饰器模块
"""
import time
import logging
import functools
from typing import Callable, Any
from datetime import datetime

def test_logger(func: Callable) -> Callable:
    """
    记录测试执行时间和结果的装饰器
    :param func: 被装饰的测试函数
    :return: 包装后的函数
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        test_name = func.__name__
        
        logging.info(f"开始执行测试: {test_name}")
        logging.info(f"开始时间: {datetime.fromtimestamp(start_time)}")
        
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            logging.info(f"测试 {test_name} 执行成功")
            logging.info(f"执行时间: {duration:.2f} 秒")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            logging.error(f"测试 {test_name} 执行失败")
            logging.error(f"错误信息: {str(e)}")
            logging.info(f"执行时间: {duration:.2f} 秒")
            
            raise
            
    return wrapper

def retry(max_attempts: int = 3, delay: float = 1.0) -> Callable:
    """
    测试重试装饰器
    :param max_attempts: 最大重试次数
    :param delay: 重试间隔(秒)
    :return: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        logging.error(f"测试 {func.__name__} 重试 {max_attempts} 次后仍然失败")
                        raise
                    logging.warning(f"测试 {func.__name__} 第 {attempts} 次重试")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def skip_if(condition: bool, reason: str = "") -> Callable:
    """
    条件跳过测试的装饰器
    :param condition: 跳过条件
    :param reason: 跳过原因
    :return: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if condition:
                logging.info(f"跳过测试 {func.__name__}: {reason}")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator 