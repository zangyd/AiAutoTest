"""
移动端测试配置文件
"""

# Android设备配置
ANDROID_CAPS = {
    'platformName': 'Android',
    'automationName': 'UiAutomator2',
    'deviceName': 'Android Emulator',
    'platformVersion': '11.0',
    'noReset': True,
    'unicodeKeyboard': True,
    'resetKeyboard': True,
    'newCommandTimeout': 6000,
    'androidInstallTimeout': 90000
}

# iOS设备配置
IOS_CAPS = {
    'platformName': 'iOS',
    'automationName': 'XCUITest',
    'deviceName': 'iPhone Simulator',
    'platformVersion': '14.5',
    'noReset': True,
    'newCommandTimeout': 6000
}

# 测试配置
TEST_CONFIG = {
    'implicit_wait': 10,  # 隐式等待时间（秒）
    'explicit_wait': 20,  # 显式等待时间（秒）
    'polling_interval': 0.5,  # 轮询间隔（秒）
    'screenshot_dir': 'screenshots',  # 截图保存目录
    'video_dir': 'videos',  # 视频保存目录
    'retry_count': 3,  # 失败重试次数
}

# 测试数据
TEST_DATA = {
    'valid_username': 'testuser',
    'valid_password': 'password123',
    'invalid_username': 'wronguser',
    'invalid_password': 'wrongpass'
} 