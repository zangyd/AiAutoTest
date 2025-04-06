"""
服务器等待工具
"""
import time
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def wait_for_server(url: str, timeout: int = 30, error_msg: str = None) -> None:
    """
    等待服务器就绪
    
    Args:
        url: 健康检查URL
        timeout: 超时时间（秒）
        error_msg: 自定义错误消息
    
    Raises:
        TimeoutError: 如果服务器在超时时间内未就绪
    """
    start_time = time.time()
    
    # 配置重试策略
    session = requests.Session()
    retries = Retry(
        total=3,  # 最大重试次数
        backoff_factor=0.5,  # 重试间隔
        status_forcelist=[500, 502, 503, 504]  # 需要重试的状态码
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    while True:
        try:
            response = session.get(url, timeout=5)
            if response.status_code == 200:
                return
        except (requests.RequestException, ConnectionError):
            pass
            
        if time.time() - start_time > timeout:
            raise TimeoutError(error_msg or f"服务器在{timeout}秒内未就绪: {url}")
            
        time.sleep(1)  # 等待1秒后重试 