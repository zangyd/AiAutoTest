"""
基础页面类，封装常用的页面操作方法
"""
import os
import yaml
from typing import Optional, Any
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.webdriver import WebDriver
import logging

logger = logging.getLogger(__name__)

class BasePage:
    """基础页面类"""

    def __init__(self, driver: WebDriver):
        """
        初始化基础页面
        
        Args:
            driver: Appium WebDriver实例
        """
        self.driver = driver
        self._load_config()
        
    def _load_config(self) -> None:
        """加载测试配置"""
        config_path = os.path.join(os.path.dirname(__file__), '../config/app_config.yaml')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.settings = config['test_settings']
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
            
    def find_element(self, locator: tuple, timeout: Optional[int] = None) -> Any:
        """
        查找元素
        
        Args:
            locator: 元素定位器，格式为(By.XX, "value")
            timeout: 超时时间(秒)，默认使用配置文件中的显式等待时间
            
        Returns:
            找到的元素
        """
        if timeout is None:
            timeout = self.settings['explicit_wait']
            
        try:
            element = WebDriverWait(
                self.driver, 
                timeout,
                self.settings['polling_interval']
            ).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except Exception as e:
            logger.error(f"查找元素失败 {locator}: {e}")
            raise
            
    def click(self, locator: tuple, timeout: Optional[int] = None) -> None:
        """
        点击元素
        
        Args:
            locator: 元素定位器
            timeout: 超时时间(秒)
        """
        element = self.find_element(locator, timeout)
        try:
            element.click()
            logger.info(f"点击元素 {locator}")
        except Exception as e:
            logger.error(f"点击元素失败 {locator}: {e}")
            raise
            
    def input_text(self, locator: tuple, text: str, timeout: Optional[int] = None) -> None:
        """
        输入文本
        
        Args:
            locator: 元素定位器
            text: 要输入的文本
            timeout: 超时时间(秒)
        """
        element = self.find_element(locator, timeout)
        try:
            element.clear()
            element.send_keys(text)
            logger.info(f"输入文本 '{text}' 到元素 {locator}")
        except Exception as e:
            logger.error(f"输入文本失败 {locator}: {e}")
            raise
            
    def get_text(self, locator: tuple, timeout: Optional[int] = None) -> str:
        """
        获取元素文本
        
        Args:
            locator: 元素定位器
            timeout: 超时时间(秒)
            
        Returns:
            元素的文本内容
        """
        element = self.find_element(locator, timeout)
        try:
            text = element.text
            logger.info(f"获取元素文本 {locator}: {text}")
            return text
        except Exception as e:
            logger.error(f"获取元素文本失败 {locator}: {e}")
            raise
            
    def is_element_present(self, locator: tuple, timeout: Optional[int] = None) -> bool:
        """
        判断元素是否存在
        
        Args:
            locator: 元素定位器
            timeout: 超时时间(秒)
            
        Returns:
            元素是否存在
        """
        try:
            self.find_element(locator, timeout)
            return True
        except:
            return False

    def find_elements(self, locator: tuple):
        """
        查找多个元素
        :param locator: 元素定位器
        :return: 找到的元素列表
        """
        try:
            elements = self.find_element(locator)
            self.logger.info(f"Found {len(elements)} elements: {locator}")
            return elements
        except Exception as e:
            self.logger.error(f"Failed to find elements {locator}: {e}")
            self.take_screenshot(f"elements_not_found_{locator[1]}")
            raise

    def take_screenshot(self, name: str):
        """
        截图
        :param name: 截图名称
        """
        try:
            screenshot_path = f"{self.settings['screenshot_dir']}/{name}.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1000):
        """
        滑动操作
        :param start_x: 起始x坐标
        :param start_y: 起始y坐标
        :param end_x: 结束x坐标
        :param end_y: 结束y坐标
        :param duration: 持续时间（毫秒）
        """
        try:
            self.driver.swipe(start_x, start_y, end_x, end_y, duration)
            self.logger.info(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        except Exception as e:
            self.logger.error(f"Failed to swipe: {e}")
            self.take_screenshot("swipe_failed")
            raise 