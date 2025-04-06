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
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        format_string: Optional[str] = None,
        console_output: bool = True,
        console_color: bool = False,
        async_mode: bool = False
    ):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_dir: 日志文件目录
            level: 日志级别
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留的备份文件数量
            format_string: 日志格式字符串
            console_output: 是否输出到控制台
            console_color: 是否启用彩色控制台输出
            async_mode: 是否启用异步日志
            
        Raises:
            OSError: 当日志目录创建失败或无权限访问时抛出
        """
        self.name = name
        self.level = level
        self.log_dir = log_dir
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.console_color = console_color
        self.async_mode = async_mode
        self.console_output = console_output
        self.handlers: List[logging.Handler] = []
        
        # 验证并创建日志目录
        log_path = Path(log_dir)
        self._ensure_log_dir(log_path)
        
        # 创建日志记录器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # 禁止日志传播
        
        # 清除已有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 设置日志格式
        format_string = "%(message)s"  # 不添加换行符
        
        # 创建文件处理器
        file_handler = RotatingFileHandler(
            filename=str(log_path / f"{name}.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8',
            mode='a'  # 使用追加模式
        )
        
        formatter = logging.Formatter(format_string)
        file_handler.setFormatter(formatter)
        
        if async_mode:
            async_handler = AsyncHandler(file_handler)
            async_handler.setFormatter(formatter)  # 确保异步处理器也有格式化器
            self.logger.addHandler(async_handler)
            self.handlers.append(async_handler)
        else:
            self.logger.addHandler(file_handler)
            self.handlers.append(file_handler)
        
        # 如果需要，添加控制台处理器
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)  # 使用 sys.stdout
            
            if console_color:
                console_formatter = ColoredFormatter(format_string)
            else:
                console_formatter = logging.Formatter(format_string)
            
            console_handler.setFormatter(console_formatter)
            
            if async_mode:
                async_handler = AsyncHandler(console_handler)
                async_handler.setFormatter(console_formatter)  # 确保异步处理器也有格式化器
                self.logger.addHandler(async_handler)
                self.handlers.append(async_handler)
            else:
                self.logger.addHandler(console_handler)
                self.handlers.append(console_handler)
        
        # 初始化过滤器列表
        self.filters: List[logging.Filter] = []
    
    def add_filter(self, filter_obj: logging.Filter) -> None:
        """
        添加日志过滤器
        
        Args:
            filter_obj: 日志过滤器对象
        """
        self.filters.append(filter_obj)
        self.logger.addFilter(filter_obj)
    
    def remove_filter(self, filter_obj: logging.Filter) -> None:
        """
        移除日志过滤器
        
        Args:
            filter_obj: 日志过滤器对象
        """
        if filter_obj in self.filters:
            self.filters.remove(filter_obj)
            self.logger.removeFilter(filter_obj)
    
    def flush(self) -> None:
        """等待所有异步日志处理完成"""
        for handler in self.handlers:
            try:
                handler.flush()
            except Exception:
                pass
    
    def close(self) -> None:
        """关闭日志记录器"""
        for handler in self.handlers:
            try:
                handler.flush()
                handler.close()
            except Exception:
                pass
    
    def _ensure_log_dir(self, path: Path) -> None:
        """
        确保日志目录存在且具有正确的权限
        
        Args:
            path: 日志目录路径
            
        Raises:
            OSError: 当目录创建失败或权限不正确时
        """
        def check_dir_permissions(p: Path) -> None:
            """检查目录权限"""
            try:
                if p.exists() and not p.is_dir():
                    raise OSError(f"指定的路径不是目录: {p}")
                
                mode = os.stat(str(p)).st_mode
                if not mode & stat.S_IRUSR or not mode & stat.S_IWUSR or not mode & stat.S_IXUSR:
                    raise OSError(f"日志目录无写入权限: {p}")
            except (OSError, PermissionError) as e:
                raise OSError(f"无法访问目录 {p}: {str(e)}")
        
        if path.exists():
            check_dir_permissions(path)
        else:
            parent = path
            while not parent.exists() and parent != parent.parent:
                parent = parent.parent
            
            if not parent.exists():
                raise OSError(f"无法创建日志目录，父目录不存在: {path}")
            
            check_dir_permissions(parent)
            
            try:
                path.mkdir(parents=True, mode=0o755)
                check_dir_permissions(path)
            except Exception as e:
                raise OSError(f"创建日志目录失败: {str(e)}")
    
    def _format_log(
        self,
        level: str,
        message: str,
        user_id: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        """
        格式化日志消息
        
        Args:
            level: 日志级别
            message: 日志消息
            user_id: 用户ID
            **kwargs: 其他日志字段
            
        Returns:
            str: 格式化后的日志消息
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "user_id": user_id,
            **kwargs
        }
        return json.dumps(log_data, ensure_ascii=False)  # 不添加换行符
    
    def debug(
        self,
        message: str,
        user_id: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        """记录DEBUG级别日志"""
        formatted_message = self._format_log("DEBUG", message, user_id, **kwargs)
        self.logger.debug(formatted_message)
        if self.console_output:
            print(formatted_message, flush=True)
        for handler in self.handlers:
            try:
                handler.flush()
            except Exception:
                pass
    
    def info(
        self,
        message: str,
        user_id: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        """记录INFO级别日志"""
        formatted_message = self._format_log("INFO", message, user_id, **kwargs)
        self.logger.info(formatted_message)
        if self.console_output:
            print(formatted_message, flush=True)
        for handler in self.handlers:
            try:
                handler.flush()
            except Exception:
                pass
    
    def warning(
        self,
        message: str,
        user_id: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        """记录WARNING级别日志"""
        formatted_message = self._format_log("WARNING", message, user_id, **kwargs)
        self.logger.warning(formatted_message)
        if self.console_output:
            print(formatted_message, flush=True)
        for handler in self.handlers:
            try:
                handler.flush()
            except Exception:
                pass
    
    def error(
        self,
        message: str,
        user_id: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        """记录ERROR级别日志"""
        formatted_message = self._format_log("ERROR", message, user_id, **kwargs)
        self.logger.error(formatted_message)
        if self.console_output:
            print(formatted_message, flush=True)
        for handler in self.handlers:
            try:
                handler.flush()
            except Exception:
                pass
    
    def critical(
        self,
        message: str,
        user_id: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        """记录CRITICAL级别日志"""
        formatted_message = self._format_log("CRITICAL", message, user_id, **kwargs)
        self.logger.critical(formatted_message)
        if self.console_output:
            print(formatted_message, flush=True)
        for handler in self.handlers:
            try:
                handler.flush()
            except Exception:
                pass
    
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