from typing import Optional, Union
from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright
from .browser_config import get_browser_config
import logging

logger = logging.getLogger(__name__)

class BrowserUtils:
    def __init__(self, browser_type: str = 'chrome'):
        """初始化浏览器工具类
        Args:
            browser_type: 浏览器类型，支持chrome/firefox/edge
        """
        self.browser_type = browser_type.lower()
        self.playwright = sync_playwright().start()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    def launch_browser(self) -> Browser:
        """启动浏览器"""
        try:
            browser_config = get_browser_config(self.browser_type)
            if self.browser_type == 'chrome':
                self.browser = self.playwright.chromium.launch(**browser_config)
            elif self.browser_type == 'firefox':
                self.browser = self.playwright.firefox.launch(**browser_config)
            elif self.browser_type == 'edge':
                self.browser = self.playwright.chromium.launch(**browser_config)
            else:
                raise ValueError(f"不支持的浏览器类型: {self.browser_type}")
            
            logger.info(f"成功启动{self.browser_type}浏览器")
            return self.browser
        except Exception as e:
            logger.error(f"启动浏览器失败: {str(e)}")
            raise
    
    def create_context(self) -> BrowserContext:
        """创建浏览器上下文"""
        if not self.browser:
            self.launch_browser()
        self.context = self.browser.new_context()
        return self.context
    
    def new_page(self) -> Page:
        """创建新页面"""
        if not self.context:
            self.create_context()
        self.page = self.context.new_page()
        return self.page
    
    def navigate(self, url: str, timeout: int = 30000) -> None:
        """导航到指定URL
        Args:
            url: 目标URL
            timeout: 超时时间(毫秒)
        """
        if not self.page:
            self.new_page()
        try:
            self.page.goto(url, timeout=timeout)
            logger.info(f"成功导航到: {url}")
        except Exception as e:
            logger.error(f"导航失败: {str(e)}")
            raise
    
    def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        """等待元素出现
        Args:
            selector: CSS选择器
            timeout: 超时时间(毫秒)
        """
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
        except Exception as e:
            logger.error(f"等待元素 {selector} 失败: {str(e)}")
            raise
    
    def click(self, selector: str, timeout: int = 30000) -> None:
        """点击元素
        Args:
            selector: CSS选择器
            timeout: 超时时间(毫秒)
        """
        try:
            self.wait_for_selector(selector, timeout)
            self.page.click(selector)
        except Exception as e:
            logger.error(f"点击元素 {selector} 失败: {str(e)}")
            raise
    
    def type(self, selector: str, text: str, timeout: int = 30000) -> None:
        """输入文本
        Args:
            selector: CSS选择器
            text: 要输入的文本
            timeout: 超时时间(毫秒)
        """
        try:
            self.wait_for_selector(selector, timeout)
            self.page.fill(selector, text)
        except Exception as e:
            logger.error(f"输入文本到元素 {selector} 失败: {str(e)}")
            raise
    
    def get_text(self, selector: str, timeout: int = 30000) -> str:
        """获取元素文本
        Args:
            selector: CSS选择器
            timeout: 超时时间(毫秒)
        Returns:
            元素文本内容
        """
        try:
            self.wait_for_selector(selector, timeout)
            return self.page.text_content(selector)
        except Exception as e:
            logger.error(f"获取元素 {selector} 文本失败: {str(e)}")
            raise
    
    def screenshot(self, path: str) -> None:
        """截图
        Args:
            path: 截图保存路径
        """
        try:
            self.page.screenshot(path=path)
            logger.info(f"截图已保存到: {path}")
        except Exception as e:
            logger.error(f"截图失败: {str(e)}")
            raise
    
    def close(self) -> None:
        """关闭浏览器及所有资源"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            self.playwright.stop()
            logger.info("浏览器资源已清理完毕")
        except Exception as e:
            logger.error(f"关闭浏览器资源失败: {str(e)}")
            raise 