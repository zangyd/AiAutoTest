"""
基础页面类，提供通用的页面操作方法
"""
from playwright.sync_api import Page
import logging
from typing import Optional, List

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self._init_logging()

    def _init_logging(self):
        """初始化日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def click(self, selector: str, timeout: int = 5000):
        """点击元素"""
        try:
            self.page.click(selector, timeout=timeout)
            self.logger.info(f"Clicked element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to click element {selector}: {e}")
            raise

    def fill(self, selector: str, value: str, timeout: int = 5000):
        """填充输入框"""
        try:
            self.page.fill(selector, value, timeout=timeout)
            self.logger.info(f"Filled {selector} with value: {value}")
        except Exception as e:
            self.logger.error(f"Failed to fill {selector}: {e}")
            raise

    def get_text(self, selector: str, timeout: int = 5000) -> str:
        """获取元素文本"""
        try:
            element = self.page.wait_for_selector(selector, timeout=timeout)
            text = element.text_content()
            self.logger.info(f"Got text from {selector}: {text}")
            return text
        except Exception as e:
            self.logger.error(f"Failed to get text from {selector}: {e}")
            raise

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """检查元素是否可见"""
        try:
            element = self.page.wait_for_selector(selector, timeout=timeout)
            return element.is_visible()
        except Exception:
            return False

    def wait_for_navigation(self, timeout: int = 5000):
        """等待页面导航完成"""
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            self.logger.info("Navigation completed")
        except Exception as e:
            self.logger.error(f"Navigation timeout: {e}")
            raise

    def take_screenshot(self, name: str):
        """截取页面截图"""
        try:
            self.page.screenshot(path=f"screenshots/{name}.png")
            self.logger.info(f"Screenshot saved: {name}.png")
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            raise 