"""
日志记录器模块

提供统一的日志记录功能
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

class Logger:
    """日志记录器类"""
    
    def __init__(self, name: str = "app"):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 确保日志目录存在
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 配置文件处理器
        file_handler = logging.FileHandler(
            filename=log_dir / f"{name}.log",
            encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        
        # 配置控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
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
        return json.dumps(log_data, ensure_ascii=False)
    
    def info(
        self,
        message: str,
        user_id: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        """
        记录INFO级别日志
        
        Args:
            message: 日志消息
            user_id: 用户ID
            **kwargs: 其他日志字段
        """
        self.logger.info(
            self._format_log("INFO", message, user_id, **kwargs)
        )
    
    def warning(
        self,
        message: str,
        user_id: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        """
        记录WARNING级别日志
        
        Args:
            message: 日志消息
            user_id: 用户ID
            **kwargs: 其他日志字段
        """
        self.logger.warning(
            self._format_log("WARNING", message, user_id, **kwargs)
        )
    
    def error(
        self,
        message: str,
        user_id: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        """
        记录ERROR级别日志
        
        Args:
            message: 日志消息
            user_id: 用户ID
            **kwargs: 其他日志字段
        """
        self.logger.error(
            self._format_log("ERROR", message, user_id, **kwargs)
        )
    
    def critical(
        self,
        message: str,
        user_id: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        """
        记录CRITICAL级别日志
        
        Args:
            message: 日志消息
            user_id: 用户ID
            **kwargs: 其他日志字段
        """
        self.logger.critical(
            self._format_log("CRITICAL", message, user_id, **kwargs)
        )

# 创建默认日志记录器实例
logger = Logger() 