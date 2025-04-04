"""
Appium驱动工具类
"""
from typing import Optional, Dict, Any
from appium import webdriver
from appium.webdriver.webdriver import WebDriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from ..config.appium_config import (
    APPIUM_SERVER,
    TIMEOUTS,
    RETRY
)
import time
import logging
from .test_utils import TestUtils

logger = logging.getLogger(__name__)

class AppiumDriver:
    """Appium驱动管理类"""
    
    def __init__(self):
        """初始化Appium驱动管理器"""
        self.driver: Optional[WebDriver] = None
        self.server_url = f"http://{APPIUM_SERVER['host']}:{APPIUM_SERVER['port']}{APPIUM_SERVER['path']}"
        
    def init_driver(self, platform: str = None, caps: Dict[str, Any] = None) -> WebDriver:
        """
        初始化Appium驱动
        
        Args:
            platform: 平台类型('Android' or 'iOS')，如果为None则从环境变量获取
            caps: 自定义capabilities配置
            
        Returns:
            WebDriver: Appium WebDriver实例
        """
        try:
            # 获取设备信息
            device_info = TestUtils.get_device_info()
            platform = platform or device_info['platformName']
            
            # 选择平台对应的配置
            if platform.lower() == 'android':
                options = UiAutomator2Options()
            else:
                options = XCUITestOptions()
            
            # 设置capabilities
            for key, value in device_info.items():
                options.set_capability(key, value)
            
            # 合并自定义配置
            if caps:
                for key, value in caps.items():
                    options.set_capability(key, value)
                
            # 创建driver实例
            for attempt in range(RETRY['max_attempts']):
                try:
                    self.driver = webdriver.Remote(
                        command_executor=self.server_url,
                        options=options
                    )
                    break
                except Exception as e:
                    if attempt == RETRY['max_attempts'] - 1:
                        raise e
                    delay = RETRY['delay'] * (RETRY['backoff'] ** attempt)
                    logger.warning(f"第{attempt + 1}次尝试创建driver失败,{delay}秒后重试: {str(e)}")
                    time.sleep(delay)
            
            # 设置超时配置
            self.driver.implicitly_wait(TIMEOUTS['implicit'])
            self.driver.set_page_load_timeout(TIMEOUTS['page_load'])
            self.driver.set_script_timeout(TIMEOUTS['script'])
            
            logger.info(f"Appium driver初始化成功: {platform}")
            return self.driver
            
        except Exception as e:
            logger.error(f"Appium driver初始化失败: {str(e)}")
            raise
            
    def quit_driver(self):
        """关闭Appium驱动"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("Appium driver已关闭")
        except Exception as e:
            logger.error(f"关闭Appium driver失败: {str(e)}")
            raise
            
    def __enter__(self):
        """上下文管理器入口"""
        self.init_driver()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.quit_driver() 