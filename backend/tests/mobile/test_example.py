import pytest
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.common.by import By
from .pages.base_page import BasePage
from .utils.test_utils import TestUtils

@pytest.mark.mobile
def test_example_app(driver: WebDriver):
    """示例测试用例"""
    base_page = BasePage(driver)
    
    # 等待应用启动
    assert base_page.is_element_present((By.ID, 'com.example.app:id/splash_screen'))
    
    # 点击登录按钮
    base_page.click((By.ID, 'com.example.app:id/login_button'))
    
    # 输入用户名和密码
    base_page.input_text((By.ID, 'com.example.app:id/username'), 'testuser')
    base_page.input_text((By.ID, 'com.example.app:id/password'), 'password123')
    
    # 点击提交
    base_page.click((By.ID, 'com.example.app:id/submit_button'))
    
    # 验证登录成功
    assert base_page.is_element_present((By.ID, 'com.example.app:id/home_screen'))
    
    # 截图
    screenshot_path = TestUtils.get_screenshot_path('test_example_app')
    base_page.screenshot(screenshot_path) 