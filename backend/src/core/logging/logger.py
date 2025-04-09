"""
统一的日志记录组件

提供完整的日志记录功能，支持文件日志、控制台输出、性能日志等特性
"""
import os
import time
import json
import stat
import queue
import logging
import threading
import colorama
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from contextlib import contextmanager
from typing import Any, Dict, Optional, List
import sys

class AsyncHandler(logging.Handler):
    """异步日志处理器"""
    
    def __init__(self, handler):
        """初始化异步处理器"""
        super().__init__()
        self.handler = handler
        self.queue = queue.Queue()
        self.closed = False
        self.event = threading.Event()
        self.thread = threading.Thread(target=self._process_logs)
        self.thread.daemon = True
        self.thread.start()
    
    def emit(self, record):
        """将日志记录放入队列"""
        if not self.closed:
            try:
                self.queue.put_nowait(record)
                self.event.set()  # 通知处理线程
            except queue.Full:
                pass  # 队列已满时丢弃日志
    
    def _process_logs(self):
        """处理队列中的日志记录"""
        while not self.closed:
            try:
                # 处理所有待处理的日志
                while not self.queue.empty():
                    record = self.queue.get_nowait()
                    try:
                        # 确保记录有正确的格式化器
                        if not record.msg and hasattr(record, 'message'):
                            record.msg = record.message
                        self.handler.emit(record)
                        self.handler.flush()  # 立即刷新
                    except Exception:
                        self.handleError(record)
                    finally:
                        self.queue.task_done()
                
                # 等待新的日志记录
                self.event.wait(0.1)
                self.event.clear()
            except Exception:
                pass  # 忽略其他异常
    
    def flush(self):
        """等待所有异步日志处理完成"""
        if self.closed:
            return
            
        try:
            # 通知处理线程
            self.event.set()
            
            # 等待队列处理完成
            self.queue.join()
            
            # 刷新底层处理器
            self.handler.flush()
        except Exception:
            pass
    
    def close(self):
        """关闭处理器"""
        if not self.closed:
            self.closed = True
            self.flush()  # 确保所有消息都被处理
            self.event.set()  # 唤醒处理线程
            self.thread.join(timeout=1.0)  # 等待处理线程结束
            self.handler.close()
            super().close()

class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    COLORS = {
        'DEBUG': colorama.Fore.BLUE,
        'INFO': colorama.Fore.GREEN,
        'WARNING': colorama.Fore.YELLOW,
        'ERROR': colorama.Fore.RED,
        'CRITICAL': colorama.Fore.RED + colorama.Style.BRIGHT
    }
    
    def format(self, record):
        """格式化日志记录"""
        # 保存原始的levelname
        original_levelname = record.levelname
        try:
            record.levelname = (
                f"{self.COLORS.get(record.levelname, '')}"
                f"{record.levelname}"
                f"{colorama.Style.RESET_ALL}"
            )
            return super().format(record)
        finally:
            # 恢复原始的levelname
            record.levelname = original_levelname

class Logger:
    """统一的日志记录器类"""
    
    def __init__(
        self,
        name: str = "app",
        log_dir: str = "logs",
        level: int = logging.INFO,
        console_output: bool = True,
        console_color: bool = False,
        async_mode: bool = False
    ):
        """初始化日志记录器"""
        self.name = name
        self.level = level
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置日志记录器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 创建JSON格式化器
        json_formatter = logging.Formatter('%(message)s')
        
        # 添加文件处理器
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f"{name}.log"),
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(json_formatter)  # 设置JSON格式化器
        
        # 如果启用异步模式，使用异步处理器包装文件处理器
        if async_mode:
            file_handler = AsyncHandler(file_handler)
            
        self.logger.addHandler(file_handler)
        
        # 如果需要，添加控制台处理器
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            if console_color:
                console_handler.setFormatter(ColoredFormatter('%(levelname)s: %(message)s'))
            else:
                console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            self.logger.addHandler(console_handler)
    
    def _log(self, level: str, message: str, *args: Any, **kwargs: Any) -> None:
        """记录日志的内部方法"""
        # 将所有kwargs作为extra数据
        formatted_message = self._format_log_message(level, message, kwargs)
        self.logger.log(getattr(logging, level), formatted_message)
        self.flush()  # 立即刷新日志

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录INFO级别的日志"""
        self._log("INFO", message, *args, **kwargs)
    
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录WARNING级别的日志"""
        self._log("WARNING", message, *args, **kwargs)
    
    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录ERROR级别的日志"""
        self._log("ERROR", message, *args, **kwargs)
    
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录DEBUG级别的日志"""
        self._log("DEBUG", message, *args, **kwargs)
    
    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录CRITICAL级别的日志"""
        self._log("CRITICAL", message, *args, **kwargs)

    def add_filter(self, filter_obj: logging.Filter) -> None:
        """
        添加日志过滤器
        
        Args:
            filter_obj: 日志过滤器对象
        """
        self.logger.addFilter(filter_obj)
    
    def remove_filter(self, filter_obj: logging.Filter) -> None:
        """
        移除日志过滤器
        
        Args:
            filter_obj: 日志过滤器对象
        """
        self.logger.removeFilter(filter_obj)
    
    def flush(self) -> None:
        """刷新所有日志处理器"""
        for handler in self.logger.handlers:
            handler.flush()
    
    def close(self) -> None:
        """关闭日志记录器"""
        for handler in self.logger.handlers:
            try:
                handler.flush()
                handler.close()
            except Exception:
                pass
    
    def _format_log_message(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """格式化日志消息为JSON格式"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "logger": self.name  # 添加logger名称以区分不同的日志来源
        }
        
        # 确保extra是字典类型
        if extra and isinstance(extra, dict):
            # 过滤掉None值，避免在JSON中出现null
            filtered_extra = {k: v for k, v in extra.items() if v is not None}
            log_data.update(filtered_extra)
        
        return json.dumps(log_data, ensure_ascii=False)

    def info_with_context(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> None:
        """
        记录带上下文的INFO级别日志
        
        Args:
            message: 日志消息
            context: 上下文信息
        """
        self.info(message, **context)
    
    @contextmanager
    def log_performance(
        self,
        operation: str,
        level: int = logging.DEBUG,
        user_id: Optional[int] = None,
        **kwargs: Any
    ):
        """
        记录操作执行时间的上下文管理器
        
        Args:
            operation: 操作名称
            level: 日志级别
            user_id: 用户ID
            **kwargs: 其他日志字段
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = (time.time() - start_time) * 1000  # 转换为毫秒
            message = f"{operation} - 耗时: {duration:.2f}ms"
            log_func = getattr(self, logging.getLevelName(level).lower())
            log_func(message, user_id=user_id, duration=duration, **kwargs)

# 创建默认日志记录器实例
logger = Logger() 