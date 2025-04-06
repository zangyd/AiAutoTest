"""
登录页面测试用例
"""
import pytest
from playwright.sync_api import Page, expect

def test_login_page_title(page: Page, base_url: str):
    """测试登录页面标题"""
    page.goto(f"{base_url}/login")
    expect(page).to_have_title("登录 - 自动化测试平台")

def test_login_success(page: Page, base_url: str):
    """测试登录成功场景"""
    # 1. 导航到登录页面
    page.goto(f"{base_url}/login")
    
    # 2. 填写登录表单
    page.fill("input[name='username']", "admin")
    page.fill("input[name='password']", "admin")
    
    # 3. 点击登录按钮
    page.click("button[type='submit']")
    
    # 4. 验证登录成功
    # 等待URL变化
    page.wait_for_url(f"{base_url}/dashboard")
    # 验证欢迎信息
    expect(page.locator(".welcome-message")).to_contain_text("欢迎回来，admin")

def test_login_failed(page: Page, base_url: str):
    """测试登录失败场景"""
    # 1. 导航到登录页面
    page.goto(f"{base_url}/login")
    
    # 2. 填写错误的登录信息
    page.fill("input[name='username']", "wrong_user")
    page.fill("input[name='password']", "wrong_password")
    
    # 3. 点击登录按钮
    page.click("button[type='submit']")
    
    # 4. 验证错误信息
    expect(page.locator(".error-message")).to_contain_text("用户名或密码错误")

@pytest.mark.skip(reason="注册功能尚未实现")
def test_register_page(page: Page, base_url: str):
    """测试注册页面（待实现）"""
    pass 