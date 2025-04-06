"""
登录功能测试用例
"""
import pytest
from ..utils.appium_driver import AppiumDriver
from ..pages.login_page import LoginPage
import logging

logger = logging.getLogger(__name__)

class TestLogin:
    """登录功能测试类"""
    
    @pytest.fixture(scope="function")
    def driver(self):
        """
        Appium驱动fixture
        
        Yields:
            WebDriver: Appium WebDriver实例
        """
        driver_manager = AppiumDriver()
        driver = driver_manager.get_driver()
        yield driver
        driver_manager.quit_driver()
        
    @pytest.fixture(scope="function")
    def login_page(self, driver):
        """
        登录页面fixture
        
        Args:
            driver: Appium WebDriver实例
            
        Returns:
            LoginPage: 登录页面实例
        """
        return LoginPage(driver)
        
    def test_login_success(self, login_page):
        """测试登录成功场景"""
        logger.info("开始测试登录成功场景")
        
        # 执行登录操作
        login_page.login("admin", "admin")
        
        # 验证登录成功
        assert not login_page.is_on_login_page(), "登录失败，仍在登录页面"
        logger.info("登录成功测试通过")
        
    def test_login_failed_wrong_password(self, login_page):
        """测试密码错误场景"""
        logger.info("开始测试密码错误场景")
        
        # 执行登录操作
        login_page.login("admin", "wrong_password")
        
        # 验证错误信息
        error_message = login_page.get_error_message()
        assert "用户名或密码错误" in error_message, f"错误信息不符合预期: {error_message}"
        assert login_page.is_on_login_page(), "未停留在登录页面"
        logger.info("密码错误测试通过")
        
    def test_login_failed_empty_username(self, login_page):
        """测试用户名为空场景"""
        logger.info("开始测试用户名为空场景")
        
        # 执行登录操作
        login_page.login("", "admin")
        
        # 验证错误信息
        error_message = login_page.get_error_message()
        assert "请输入用户名" in error_message, f"错误信息不符合预期: {error_message}"
        assert login_page.is_on_login_page(), "未停留在登录页面"
        logger.info("用户名为空测试通过") 