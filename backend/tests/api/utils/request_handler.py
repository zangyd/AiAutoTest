"""
API请求处理工具
"""
import json
import logging
from typing import Dict, Any, Optional
import httpx
from ..config.api_config import API_SERVER, RETRY_CONFIG, DEFAULT_HEADERS

logger = logging.getLogger(__name__)

class RequestHandler:
    """API请求处理类"""
    
    def __init__(self, base_url: str = None, headers: Dict = None):
        """
        初始化请求处理器
        
        Args:
            base_url: API基础URL
            headers: 自定义请求头
        """
        self.base_url = base_url or f"{API_SERVER['host']}:{API_SERVER['port']}"
        self.headers = headers or DEFAULT_HEADERS.copy()
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=API_SERVER['timeout'],
            verify=API_SERVER['verify_ssl']
        )
        
    def _handle_response(self, response: httpx.Response) -> Dict:
        """
        处理API响应
        
        Args:
            response: httpx响应对象
            
        Returns:
            Dict: 处理后的响应数据
        """
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP错误: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            raise
            
    def get(self, url: str, params: Optional[Dict] = None) -> Dict:
        """
        发送GET请求
        
        Args:
            url: 请求URL
            params: URL参数
            
        Returns:
            Dict: 响应数据
        """
        response = self.client.get(url, params=params)
        return self._handle_response(response)
        
    def post(self, url: str, data: Dict = None, json_data: Dict = None) -> Dict:
        """
        发送POST请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json_data: JSON数据
            
        Returns:
            Dict: 响应数据
        """
        response = self.client.post(url, data=data, json=json_data)
        return self._handle_response(response)
        
    def put(self, url: str, data: Dict = None, json_data: Dict = None) -> Dict:
        """
        发送PUT请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json_data: JSON数据
            
        Returns:
            Dict: 响应数据
        """
        response = self.client.put(url, data=data, json=json_data)
        return self._handle_response(response)
        
    def delete(self, url: str) -> Dict:
        """
        发送DELETE请求
        
        Args:
            url: 请求URL
            
        Returns:
            Dict: 响应数据
        """
        response = self.client.delete(url)
        return self._handle_response(response)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close() 