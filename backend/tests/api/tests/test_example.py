"""
API测试示例
"""
import pytest
from ..utils.request_handler import RequestHandler

def test_get_endpoint(api_client, test_environment):
    """
    测试GET请求示例
    """
    # 准备测试数据
    endpoint = "/api/test"
    expected_status = 200
    
    # 发送请求
    response = api_client.get(endpoint)
    
    # 验证响应
    assert response is not None
    assert response.get('status') == expected_status

def test_post_endpoint(api_client, auth_token):
    """
    测试POST请求示例
    """
    # 准备测试数据
    endpoint = "/api/test"
    test_data = {
        "name": "test",
        "value": "test_value"
    }
    
    # 设置认证头
    api_client.headers['Authorization'] = f"Bearer {auth_token}"
    
    # 发送请求
    response = api_client.post(endpoint, json_data=test_data)
    
    # 验证响应
    assert response is not None
    assert response.get('data') == test_data

@pytest.mark.parametrize("test_input,expected", [
    ({"id": 1}, {"status": "success"}),
    ({"id": 2}, {"status": "success"}),
])
def test_parametrized_request(api_client, test_input, expected):
    """
    参数化测试示例
    """
    # 准备测试数据
    endpoint = "/api/test"
    
    # 发送请求
    response = api_client.post(endpoint, json_data=test_input)
    
    # 验证响应
    assert response.get('status') == expected['status'] 