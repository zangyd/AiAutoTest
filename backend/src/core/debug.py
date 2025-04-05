import sys
import logging
import traceback
from functools import wraps
from typing import Any, Callable, Dict, Optional
from loguru import logger

class DebugConfig:
    """调试配置类"""
    
    def __init__(self):
        self.DEBUG = True
        self.TRACE_LEVEL = 5
        self.LOG_LEVEL = "DEBUG"
        self.VARIABLE_WATCH = {}
        self.BREAKPOINTS = set()
        
        # 配置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """配置日志系统"""
        logger.remove()  # 移除默认处理器
        
        # 添加控制台处理器
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=self.LOG_LEVEL,
            backtrace=True,
            diagnose=True
        )
        
        # 添加文件处理器
        logger.add(
            "logs/debug.log",
            rotation="500 MB",
            retention="10 days",
            compression="zip",
            level=self.LOG_LEVEL
        )

class DebugTools:
    """调试工具类"""
    
    def __init__(self, config: DebugConfig):
        self.config = config
        self.call_stack = []
        self.watch_variables = {}
    
    def watch_variable(self, name: str, value: Any):
        """监视变量值变化"""
        if name in self.watch_variables:
            old_value = self.watch_variables[name]
            if old_value != value:
                logger.debug(f"变量 {name} 的值从 {old_value} 变为 {value}")
        self.watch_variables[name] = value
    
    def set_breakpoint(self, filename: str, line: int):
        """设置断点"""
        self.config.BREAKPOINTS.add((filename, line))
        logger.debug(f"在 {filename}:{line} 设置断点")
    
    def remove_breakpoint(self, filename: str, line: int):
        """移除断点"""
        self.config.BREAKPOINTS.discard((filename, line))
        logger.debug(f"移除 {filename}:{line} 的断点")
    
    def trace_function(self, frame, event, arg):
        """跟踪函数执行"""
        if event == 'call':
            self.call_stack.append(frame)
            logger.trace(f"进入函数: {frame.f_code.co_name}")
        elif event == 'return':
            self.call_stack.pop()
            logger.trace(f"离开函数: {frame.f_code.co_name}")
        return self.trace_function

def debug_decorator(func: Callable) -> Callable:
    """调试装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"调用函数 {func.__name__} 开始")
        logger.debug(f"参数: args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数 {func.__name__} 返回值: {result}")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 发生异常: {str(e)}")
            logger.error(f"异常堆栈: {traceback.format_exc()}")
            raise
    return wrapper

class PerformanceMonitor:
    """性能监控类"""
    
    def __init__(self):
        self.function_times = {}
        self.memory_usage = {}
    
    def start_monitor(self, name: str):
        """开始监控"""
        import time
        import psutil
        
        self.function_times[name] = {
            'start_time': time.time(),
            'start_memory': psutil.Process().memory_info().rss
        }
    
    def end_monitor(self, name: str):
        """结束监控"""
        import time
        import psutil
        
        if name in self.function_times:
            start_data = self.function_times[name]
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            
            execution_time = end_time - start_data['start_time']
            memory_change = end_memory - start_data['start_memory']
            
            logger.debug(f"{name} 执行时间: {execution_time:.4f}秒")
            logger.debug(f"{name} 内存变化: {memory_change / 1024 / 1024:.2f}MB")

# 创建全局调试工具实例
debug_config = DebugConfig()
debug_tools = DebugTools(debug_config)
performance_monitor = PerformanceMonitor()

# 示例使用
if __name__ == "__main__":
    @debug_decorator
    def example_function(a: int, b: int) -> int:
        debug_tools.watch_variable("a", a)
        debug_tools.watch_variable("b", b)
        performance_monitor.start_monitor("example_function")
        result = a + b
        performance_monitor.end_monitor("example_function")
        return result
    
    # 设置断点示例
    debug_tools.set_breakpoint(__file__, 42)
    
    # 调用示例函数
    result = example_function(1, 2)
    logger.info(f"计算结果: {result}") 