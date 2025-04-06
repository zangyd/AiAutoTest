"""
Appium驱动管理类
"""
import os
from typing import Dict, Optional
from appium import webdriver
from appium.webdriver.webdriver import WebDriver
import yaml
import logging

logger = logging.getLogger(__name__)

class AppiumDriver:
    """Appium驱动管理类"""
    
    def __init__(self):
        self.driver: Optional[WebDriver] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """加载Appium配置"""
        config_path = os.path.join(os.path.dirname(__file__), '../config/app_config.yaml')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def get_driver(self) -> WebDriver:
        """
        获取Appium驱动实例
        
        Returns:
            WebDriver: Appium WebDriver实例
        """
        if not self.driver:
            try:
                # 从环境变量获取Appium服务器地址，默认为本地地址
                appium_host = os.getenv('APPIUM_HOST', 'localhost')
                appium_port = int(os.getenv('APPIUM_PORT', '4723'))
                server_url = f'http://{appium_host}:{appium_port}/wd/hub'
                
                # 创建driver实例
                self.driver = webdriver.Remote(server_url, self.config['capabilities'])
                logger.info("Appium driver创建成功")
            except Exception as e:
                logger.error(f"创建Appium driver失败: {e}")
                raise
        return self.driver
    
    def quit_driver(self) -> None:
        """关闭Appium驱动"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Appium driver已关闭")
            except Exception as e:
                logger.error(f"关闭Appium driver失败: {e}")
            finally:
                self.driver = None 