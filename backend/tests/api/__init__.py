"""
API测试包

包含API接口测试相关的配置、工具和测试用例
"""

from .config.test_config import test_settings
from .utils.test_client import TestClient

__all__ = ['test_settings', 'TestClient'] 