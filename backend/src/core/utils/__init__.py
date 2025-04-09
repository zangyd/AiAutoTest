"""
工具模块，提供文件处理等通用功能。

Features:
    - FileManager: 异步文件管理工具，支持文件的基本操作、压缩、加密等功能
    - Logger: 日志记录工具，支持文件和控制台输出，支持日志轮转和彩色输出
    - Singleton: 单例模式工具，提供类级别的单例实现
"""

from .file_manager import FileManager
from .logger import Logger
from .singleton import Singleton

__all__ = ['FileManager', 'Logger', 'Singleton'] 