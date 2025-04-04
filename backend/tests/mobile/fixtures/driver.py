import pytest
from appium import webdriver
from typing import Generator
from ..appium.config import get_config
from ..utils.test_utils import TestUtils

@pytest.fixture(scope="function")
def driver() -> Generator[webdriver.Remote, None, None]:
    """创建Appium WebDriver实例"""
    # 获取基础配置
    config = get_config()
    
    # 合并设备信息
    config.update(TestUtils.get_device_info())
    
    # 创建driver实例
    driver = webdriver.Remote(
        command_executor='http://localhost:4723/wd/hub',
        desired_capabilities=config
    )
    
    # 设置隐式等待时间
    driver.implicitly_wait(10)
    
    yield driver
    
    # 测试结束后关闭driver
    driver.quit() 