"""
测试配置管理

管理测试相关的配置项，包括API地址、超时时间等
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class TestSettings(BaseSettings):
    """测试配置类"""
    
    model_config = ConfigDict(env_prefix="TEST_")
    
    # API配置
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    API_PROTOCOL: str = "http"
    API_VERSION: str = "v1"
    
    # 测试用户配置
    TEST_USERNAME: str = "admin"
    TEST_PASSWORD: str = "admin"
    TEST_EMAIL: str = "admin@example.com"
    
    # 超时配置
    REQUEST_TIMEOUT: int = 10  # 请求超时时间（秒）
    WAIT_TIMEOUT: int = 30     # 等待超时时间（秒）
    
    @property
    def api_base_url(self) -> str:
        """API基础URL"""
        return f"{self.API_PROTOCOL}://{self.API_HOST}:{self.API_PORT}/api/{self.API_VERSION}"


# 创建全局测试配置实例
test_settings = TestSettings() 