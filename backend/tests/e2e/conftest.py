"""
全局测试配置和fixture
"""
import pytest
from typing import Generator
import subprocess
import time
import os
import signal
from playwright.sync_api import Browser, BrowserContext, Page
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from utils.drivers.browser_driver import BrowserDriver
from config.browser.playwright_config import BROWSER_CONFIG
from utils.wait_for_server import wait_for_server
from config.test_env import SERVER_CONFIG

def is_server_ready(url: str, timeout: int = 1) -> bool:
    """检查服务器是否就绪"""
    try:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.1)
        session.mount('http://', HTTPAdapter(max_retries=retries))
        response = session.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

@pytest.fixture(scope="session", autouse=True)
def web_server():
    """启动Web服务器"""
    # 切换到前端目录
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../frontend"))
    
    # 如果环境变量指定了不启动服务器，则跳过
    if os.getenv('TEST_SKIP_SERVER_START', '').lower() == 'true':
        yield None
        return
    
    # 启动服务器进程
    server_process = subprocess.Popen(
        SERVER_CONFIG['start_command'],
        shell=True,
        cwd=frontend_dir,
        preexec_fn=os.setsid  # 使用进程组
    )
    
    try:
        # 等待服务器就绪
        wait_for_server(
            url=SERVER_CONFIG['health_check_url'],
            timeout=SERVER_CONFIG['wait_timeout'],
            error_msg="前端服务器未就绪，请确保服务已启动"
        )
        
        yield server_process
        
    finally:
        # 关闭服务器进程
        if server_process:
            os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
            server_process.wait()

@pytest.fixture(scope="session")
def browser_driver():
    """创建浏览器驱动实例"""
    with BrowserDriver() as driver:
        yield driver

@pytest.fixture(scope="session")
def browser(browser_driver) -> Browser:
    """创建浏览器实例"""
    browser = browser_driver.create_browser(
        browser_type=BROWSER_CONFIG['browser_type'],
        **BROWSER_CONFIG['launch_options']
    )
    yield browser

@pytest.fixture(scope="module")
def browser_context(browser) -> BrowserContext:
    """创建浏览器上下文"""
    context = browser.new_context(**BROWSER_CONFIG['context_options'])
    yield context
    context.close()

@pytest.fixture
def page(browser_context) -> Page:
    """创建新页面"""
    page = browser_context.new_page()
    page.set_default_timeout(BROWSER_CONFIG['page_options']['timeout'])
    page.set_default_navigation_timeout(BROWSER_CONFIG['page_options']['timeout'])
    yield page
    page.close()

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "headless": True
    }

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": True
    }

@pytest.fixture(scope="session")
def base_url() -> str:
    """返回基础URL"""
    return SERVER_CONFIG['base_url'] 