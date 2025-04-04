"""
测试Appium服务器和驱动的设置
"""
import pytest
from backend.tests.mobile.utils.appium_server import AppiumServer
from backend.tests.mobile.utils.appium_driver import AppiumDriver
from backend.tests.mobile.utils.test_utils import TestUtils

def test_appium_server_setup():
    """测试Appium服务器的启动和停止"""
    server = AppiumServer()
    try:
        # 启动服务器
        assert server.start_server(), "Appium服务器启动失败"
        
        # 验证服务器是否正在运行
        assert server._is_server_running(), "Appium服务器未在运行"
    finally:
        # 停止服务器
        server.stop_server()
        assert not server._is_server_running(), "Appium服务器未正确停止"

def test_appium_driver_setup():
    """测试Appium驱动的初始化"""
    with AppiumServer() as server:
        assert server._is_server_running(), "Appium服务器未启动"
        
        with AppiumDriver() as driver:
            # 获取设备信息
            device_info = TestUtils.get_device_info()
            
            # 验证驱动是否正确初始化
            assert driver.driver is not None, "Appium驱动未正确初始化"
            
            # 验证设备平台
            assert driver.driver.capabilities['platformName'].lower() == \
                   device_info['platformName'].lower(), "设备平台不匹配"

if __name__ == '__main__':
    pytest.main(['-v', __file__]) 