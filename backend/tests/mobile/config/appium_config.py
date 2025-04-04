"""
Appium服务器配置文件
"""
from typing import Dict, Any

# Appium服务器配置
APPIUM_SERVER = {
    'host': '127.0.0.1',
    'port': 4723,
    'path': ''  # Appium 2.0不再需要/wd/hub路径
}

# 超时配置(秒)
TIMEOUTS = {
    'implicit': 10,
    'explicit': 20,
    'page_load': 30,
    'script': 30
}

# 重试配置
RETRY = {
    'max_attempts': 3,
    'delay': 1,
    'backoff': 2
} 