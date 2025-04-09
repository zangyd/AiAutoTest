"""
日志工具模块
"""
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Optional
from core.config.settings import settings

class Logger:
    """日志记录器类"""
    
    def __init__(
        self,
        name: str,
        log_dir: Optional[str] = None,
        level: int = logging.INFO,
        console_output: bool = True,
        console_color: bool = True,
        async_mode: bool = False
    ):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_dir: 日志文件目录，默认使用配置中的LOG_DIR
            level: 日志级别
            console_output: 是否输出到控制台
            console_color: 是否使用彩色输出
            async_mode: 是否使用异步模式
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 设置日志格式
        formatter = logging.Formatter(
            settings.LOG_FORMAT,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # 设置日志文件
        if log_dir is None:
            log_dir = settings.LOG_DIR
            
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, f"{name}.log")
        file_handler = TimedRotatingFileHandler(
            log_file,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 设置控制台输出
        if console_output:
            console_handler = logging.StreamHandler()
            if console_color:
                formatter = ColoredFormatter(settings.LOG_FORMAT)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def debug(self, msg: str, *args, **kwargs):
        """记录调试级别日志"""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """记录信息级别日志"""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """记录警告级别日志"""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """记录错误级别日志"""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """记录严重错误级别日志"""
        self.logger.critical(msg, *args, **kwargs)

class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """格式化日志记录"""
        # 保存原始的levelname
        levelname = record.levelname
        # 添加颜色
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record) 