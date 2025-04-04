import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from typing import Generator
from ..playwright.config import get_config

@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    """创建浏览器实例"""
    config = get_config()
    playwright = sync_playwright().start()
    browser = getattr(playwright, config['browser']).launch(**config['use'])
    yield browser
    browser.close()
    playwright.stop()

@pytest.fixture
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """创建浏览器上下文"""
    config = get_config()
    context = browser.new_context(**{k: v for k, v in config['use'].items() if k != 'headless'})
    yield context
    context.close()

@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """创建页面实例"""
    config = get_config()
    page = context.new_page()
    page.set_default_timeout(config['timeout'])
    yield page
    page.close() 