"""
配置管理模块

负责管理系统的各项配置:
- JWT配置
- 数据库配置
- Redis配置
- 日志配置
"""

from .settings import settings

__all__ = ["settings"] 