from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from typing import Optional, Any

class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        
    def find_element(self, locator: tuple) -> Any:
        """查找元素"""
        return self.wait.until(EC.presence_of_element_located(locator))
        
    def find_elements(self, locator: tuple) -> list:
        """查找多个元素"""
        return self.wait.until(EC.presence_of_all_elements_located(locator))
        
    def click(self, locator: tuple) -> None:
        """点击元素"""
        self.find_element(locator).click()
        
    def input_text(self, locator: tuple, text: str) -> None:
        """输入文本"""
        self.find_element(locator).send_keys(text)
        
    def get_text(self, locator: tuple) -> str:
        """获取元素文本"""
        return self.find_element(locator).text
        
    def is_element_present(self, locator: tuple, timeout: int = 10) -> bool:
        """判断元素是否存在"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except:
            return False
            
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = None) -> None:
        """滑动屏幕"""
        self.driver.swipe(start_x, start_y, end_x, end_y, duration)
        
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