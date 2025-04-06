"""
测试客户端

提供API测试所需的HTTP客户端功能
"""

import httpx
import logging
from typing import Optional, Dict, Any

from ..config.test_config import test_settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestClient:
    """测试客户端类"""
    
    def __init__(self):
        """初始化测试客户端"""
        self.base_url = test_settings.api_base_url
        self.token: Optional[str] = None
        self.client = httpx.Client(timeout=test_settings.REQUEST_TIMEOUT)
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头
        
        Returns:
            Dict[str, str]: 包含认证信息的请求头
        """
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    async def login(self, username: str = test_settings.TEST_USERNAME,
                   password: str = test_settings.TEST_PASSWORD) -> Dict[str, Any]:
        """登录并获取token
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Dict[str, Any]: 登录响应数据
        """
        data = {
            "username": username,
            "password": password
        }
        
        response = self.client.post(
            f"{self.base_url}/auth/login",
            json=data
        )
        response.raise_for_status()
        
        response_data = response.json()
        self.token = response_data.get("access_token")
        return response_data
    
    async def logout(self) -> None:
        """登出并清除token"""
        if self.token:
            try:
                response = self.client.post(
                    f"{self.base_url}/auth/logout",
                    headers=self._get_headers()
                )
                response.raise_for_status()
            except Exception as e:
                logger.error(f"登出失败: {str(e)}")
            finally:
                self.token = None
    
    def get(self, path: str, **kwargs) -> httpx.Response:
        """发送GET请求
        
        Args:
            path: API路径
            **kwargs: 其他请求参数
            
        Returns:
            httpx.Response: 响应对象
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self.client.get(url, headers=self._get_headers(), **kwargs)
    
    def post(self, path: str, **kwargs) -> httpx.Response:
        """发送POST请求
        
        Args:
            path: API路径
            **kwargs: 其他请求参数
            
        Returns:
            httpx.Response: 响应对象
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self.client.post(url, headers=self._get_headers(), **kwargs)
    
    def put(self, path: str, **kwargs) -> httpx.Response:
        """发送PUT请求
        
        Args:
            path: API路径
            **kwargs: 其他请求参数
            
        Returns:
            httpx.Response: 响应对象
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self.client.put(url, headers=self._get_headers(), **kwargs)
    
    def delete(self, path: str, **kwargs) -> httpx.Response:
        """发送DELETE请求
        
        Args:
            path: API路径
            **kwargs: 其他请求参数
            
        Returns:
            httpx.Response: 响应对象
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self.client.delete(url, headers=self._get_headers(), **kwargs)
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.client.close() 