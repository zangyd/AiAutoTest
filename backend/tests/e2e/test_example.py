import pytest
from playwright.sync_api import Page
from .pages.base_page import BasePage
from .utils.test_utils import TestUtils

@pytest.mark.e2e
@pytest.mark.ui
def test_example_page(page: Page):
    """示例测试用例"""
    base_page = BasePage(page)
    
    # 导航到测试页面
    base_page.navigate('http://localhost:3000')
    
    # 验证页面标题
    assert page.title() == 'AutoTest'
    
    # 截图
    screenshot_path = TestUtils.get_screenshot_path('test_example')
    base_page.screenshot(screenshot_path) 