"""
API测试固件
"""
import pytest
from ..utils.request_handler import RequestHandler
from ..config.api_config import API_SERVER, ENVIRONMENTS

@pytest.fixture(scope="session")
def api_client():
    """
    创建API客户端实例
    """
    with RequestHandler() as client:
        yield client

@pytest.fixture(scope="function")
def auth_token(api_client):
    """
    获取认证token
    """
    # 这里实现获取token的逻辑
    token = "test_token"  # 实际项目中需要通过认证接口获取
    return token

@pytest.fixture(scope="session")
def test_environment():
    """
    设置测试环境配置
    """
    return ENVIRONMENTS['test']

@pytest.fixture(scope="function")
def cleanup_test_data():
    """
    清理测试数据
    """
    # 在测试前执行的操作
    yield
    # 在测试后执行清理操作
    pass 