from playwright.sync_api import Page
from typing import Optional, Any

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        
    def navigate(self, url: str) -> None:
        """导航到指定URL"""
        self.page.goto(url)
        
    def click(self, selector: str) -> None:
        """点击元素"""
        self.page.click(selector)
        
    def fill(self, selector: str, value: str) -> None:
        """填充输入框"""
        self.page.fill(selector, value)
        
    def get_text(self, selector: str) -> str:
        """获取元素文本"""
        return self.page.text_content(selector)
        
    def is_visible(self, selector: str) -> bool:
        """检查元素是否可见"""
        return self.page.is_visible(selector)
        
    def wait_for_selector(self, selector: str, timeout: Optional[float] = None) -> Any:
        """等待元素出现"""
        return self.page.wait_for_selector(selector, timeout=timeout)
        
    def screenshot(self, path: str) -> None:
        """截图"""
        self.page.screenshot(path=path)
        
    def get_by_test_id(self, test_id: str) -> Any:
        """通过test-id获取元素"""
        return self.page.get_by_test_id(test_id)
        
    def get_by_role(self, role: str, name: Optional[str] = None) -> Any:
        """通过角色获取元素"""
        return self.page.get_by_role(role, name=name)
        
    def get_by_label(self, label: str) -> Any:
        """通过label获取元素"""
        return self.page.get_by_label(label) 