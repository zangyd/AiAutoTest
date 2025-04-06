"""
测试环境配置
"""
import os
from typing import Dict

def get_server_config() -> Dict[str, str]:
    """
    获取服务器配置
    
    支持从环境变量覆盖默认配置:
    - TEST_FRONTEND_HOST: 前端服务主机地址
    - TEST_FRONTEND_PORT: 前端服务端口
    - TEST_FRONTEND_PROTOCOL: 前端服务协议(http/https)
    - TEST_START_COMMAND: 启动前端服务的命令
    """
    # 从环境变量获取配置，如果没有则使用默认值
    host = os.getenv('TEST_FRONTEND_HOST', 'localhost')
    port = os.getenv('TEST_FRONTEND_PORT', '5173')
    protocol = os.getenv('TEST_FRONTEND_PROTOCOL', 'http')
    base_url = f"{protocol}://{host}:{port}"
    
    return {
        'base_url': base_url,
        'health_check_url': f"{base_url}/health",
        'wait_timeout': int(os.getenv('TEST_WAIT_TIMEOUT', '30')),
        'start_command': os.getenv('TEST_START_COMMAND', 'npm run dev')
    }

# 导出服务器配置
SERVER_CONFIG = get_server_config() 