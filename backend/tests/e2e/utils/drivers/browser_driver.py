"""
浏览器驱动管理类
"""
from typing import Optional
from playwright.sync_api import sync_playwright, Browser

class BrowserDriver:
    """浏览器驱动管理类"""
    
    def __init__(self):
        self._playwright = None
        self._browser = None
    
    def __enter__(self):
        """进入上下文管理器"""
        self._playwright = sync_playwright().start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
    
    def create_browser(self, browser_type: str = 'chromium', **kwargs) -> Browser:
        """
        创建浏览器实例
        
        Args:
            browser_type: 浏览器类型，支持 'chromium'、'firefox'、'webkit'
            **kwargs: 浏览器启动参数
        
        Returns:
            Browser: 浏览器实例
        """
        if not self._playwright:
            raise RuntimeError("Playwright未初始化")
            
        launcher = getattr(self._playwright, browser_type)
        if not launcher:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")
            
        self._browser = launcher.launch(**kwargs)
        return self._browser 