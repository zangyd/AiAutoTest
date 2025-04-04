"""
API测试配置文件
"""

# API服务配置
API_SERVER = {
    'host': 'http://localhost',  # API服务器地址
    'port': 8000,               # API服务器端口
    'timeout': 30,              # 请求超时时间（秒）
    'verify_ssl': False,        # 是否验证SSL证书
}

# 请求重试配置
RETRY_CONFIG = {
    'max_retries': 3,          # 最大重试次数
    'retry_delay': 1,          # 重试延迟（秒）
    'backoff_factor': 2,       # 重试延迟递增因子
}

# 请求头配置
DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

# 环境配置
ENVIRONMENTS = {
    'dev': {
        'host': 'http://dev-api.example.com',
        'auth_enabled': True,
    },
    'test': {
        'host': 'http://test-api.example.com',
        'auth_enabled': True,
    },
    'prod': {
        'host': 'http://api.example.com',
        'auth_enabled': True,
    }
}

# 认证配置
AUTH_CONFIG = {
    'token_url': '/api/auth/token',
    'refresh_url': '/api/auth/refresh',
    'token_type': 'Bearer',
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'api_test.log',
} 