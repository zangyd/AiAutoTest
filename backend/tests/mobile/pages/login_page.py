"""
登录页面类，封装登录页面的元素定位和操作方法
"""
from appium.webdriver.common.appiumby import AppiumBy
from .base_page import BasePage
import logging

logger = logging.getLogger(__name__)

class LoginPage(BasePage):
    """登录页面类"""
    
    def __init__(self, driver):
        """
        初始化登录页面
        
        Args:
            driver: Appium WebDriver实例
        """
        super().__init__(driver)
        
        # 页面元素定位器
        self._username_input = (AppiumBy.ID, "username_input")
        self._password_input = (AppiumBy.ID, "password_input")
        self._login_button = (AppiumBy.ID, "login_button")
        self._error_message = (AppiumBy.ID, "error_message")
        
    def input_username(self, username: str) -> None:
        """
        输入用户名
        
        Args:
            username: 用户名
        """
        self.input_text(self._username_input, username)
        logger.info(f"输入用户名: {username}")
        
    def input_password(self, password: str) -> None:
        """
        输入密码
        
        Args:
            password: 密码
        """
        self.input_text(self._password_input, password)
        logger.info(f"输入密码: {password}")
        
    def click_login(self) -> None:
        """点击登录按钮"""
        self.click(self._login_button)
        logger.info("点击登录按钮")
        
    def get_error_message(self) -> str:
        """
        获取错误信息
        
        Returns:
            错误信息文本
        """
        return self.get_text(self._error_message)
        
    def login(self, username: str, password: str) -> None:
        """
        执行登录操作
        
        Args:
            username: 用户名
            password: 密码
        """
        self.input_username(username)
        self.input_password(password)
        self.click_login()
        logger.info(f"执行登录操作: 用户名={username}")
        
    def is_on_login_page(self) -> bool:
        """
        判断是否在登录页面
        
        Returns:
            是否在登录页面
        """
        return self.is_element_present(self._username_input) 