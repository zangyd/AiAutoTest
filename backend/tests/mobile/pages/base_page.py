"""
移动端测试基础页面类
"""
from typing import Optional, Tuple, Any
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ..config.appium_config import TIMEOUTS
import logging

logger = logging.getLogger(__name__)

class BasePage:
    """移动端测试基础页面类"""
    
    def __init__(self, driver: WebDriver):
        """
        初始化基础页面
        
        Args:
            driver: Appium WebDriver实例
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, TIMEOUTS['explicit'])
        
    def find_element(self, locator: Tuple[str, str], timeout: int = None) -> Optional[Any]:
        """
        查找单个元素
        
        Args:
            locator: 元素定位器,格式为(定位方式, 定位值)
            timeout: 超时时间(秒)
            
        Returns:
            找到的元素或None
        """
        try:
            timeout = timeout or TIMEOUTS['explicit']
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            logger.warning(f"未找到元素: {locator}")
            return None
        except Exception as e:
            logger.error(f"查找元素失败: {str(e)}")
            raise
            
    def find_elements(self, locator: tuple) -> list:
        """查找多个元素"""
        return self.wait.until(EC.presence_of_all_elements_located(locator))
        
    def click(self, locator: Tuple[str, str], timeout: int = None) -> bool:
        """
        点击元素
        
        Args:
            locator: 元素定位器
            timeout: 超时时间(秒)
            
        Returns:
            是否点击成功
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                element.click()
                return True
            return False
        except Exception as e:
            logger.error(f"点击元素失败: {str(e)}")
            return False
            
    def input_text(self, locator: Tuple[str, str], text: str, timeout: int = None) -> bool:
        """
        输入文本
        
        Args:
            locator: 元素定位器
            text: 要输入的文本
            timeout: 超时时间(秒)
            
        Returns:
            是否输入成功
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                element.clear()
                element.send_keys(text)
                return True
            return False
        except Exception as e:
            logger.error(f"输入文本失败: {str(e)}")
            return False
            
    def get_text(self, locator: Tuple[str, str], timeout: int = None) -> Optional[str]:
        """
        获取元素文本
        
        Args:
            locator: 元素定位器
            timeout: 超时时间(秒)
            
        Returns:
            元素文本或None
        """
        try:
            element = self.find_element(locator, timeout)
            return element.text if element else None
        except Exception as e:
            logger.error(f"获取文本失败: {str(e)}")
            return None
            
    def is_element_present(self, locator: Tuple[str, str], timeout: int = None) -> bool:
        """
        判断元素是否存在
        
        Args:
            locator: 元素定位器
            timeout: 超时时间(秒)
            
        Returns:
            元素是否存在
        """
        return bool(self.find_element(locator, timeout))
            
    def swipe(self, start_x: float, start_y: float, end_x: float, end_y: float, duration: int = None):
        """
        滑动操作
        
        Args:
            start_x: 起始x坐标(相对比例,0-1)
            start_y: 起始y坐标(相对比例,0-1)
            end_x: 结束x坐标(相对比例,0-1)
            end_y: 结束y坐标(相对比例,0-1)
            duration: 持续时间(毫秒)
        """
        try:
            # 获取屏幕尺寸
            size = self.driver.get_window_size()
            width = size['width']
            height = size['height']
            
            # 计算实际坐标
            start_x = int(width * start_x)
            start_y = int(height * start_y)
            end_x = int(width * end_x)
            end_y = int(height * end_y)
            
            # 执行滑动
            self.driver.swipe(start_x, start_y, end_x, end_y, duration or 500)
        except Exception as e:
            logger.error(f"滑动操作失败: {str(e)}")
            raise
        
    def tap(self, positions: list, duration: Optional[int] = None) -> None:
        """点击坐标"""
        self.driver.tap(positions, duration)
        
    def back(self) -> None:
        """返回上一页"""
        self.driver.back()
        
    def get_window_size(self) -> dict:
        """获取屏幕尺寸"""
        return self.driver.get_window_size()
        
    def screenshot(self, filename: str) -> bool:
        """截图"""
        return self.driver.get_screenshot_as_file(filename) 