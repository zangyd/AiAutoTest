import json
import os
import requests
import pytest

def load_config():
    config_path = '/data/projects/autotest/backend/config/appium_config.json'
    with open(config_path) as f:
        return json.load(f)

def test_appium_server_connection():
    """测试Appium服务器连接"""
    try:
        config = load_config()
        server_url = f"http://{config['server']['address']}:{config['server']['port']}/status"
        
        # 直接使用requests检查Appium服务器状态
        response = requests.get(server_url)
        assert response.status_code == 200
        
        # 验证服务器状态
        status = response.json()
        assert status['value']['ready'] == True
        
    except requests.exceptions.ConnectionError:
        pytest.fail("无法连接到Appium服务器")
    except Exception as e:
        pytest.fail(f"Appium服务器连接失败: {str(e)}")

if __name__ == '__main__':
    pytest.main([__file__, '-v']) 