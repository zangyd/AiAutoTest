import pytest
from playwright.sync_api import sync_playwright
from appium import webdriver
from appium.options.android import UiAutomator2Options
import cv2
import numpy as np

def test_playwright_environment():
    """测试Playwright环境配置"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('https://www.baidu.com')
        assert page.title() == "百度一下，你就知道"
        browser.close()

def test_appium_environment():
    """测试Appium Android环境配置"""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "OCE-AN10"
    options.udid = "UJN0221227005802"
    
    try:
        driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
        print("设备已连接")
        print(f"设备信息: {driver.capabilities}")
        driver.quit()
        assert True
    except Exception as e:
        print(f"连接错误: {str(e)}")
        pytest.fail(f"Appium连接失败: {str(e)}")

def test_opencv_environment():
    """测试OpenCV环境配置"""
    # 创建一个简单的图像
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    # 画一个白色的圆
    cv2.circle(img, (50, 50), 40, (255, 255, 255), -1)
    assert img is not None
    assert img.shape == (100, 100, 3)

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 