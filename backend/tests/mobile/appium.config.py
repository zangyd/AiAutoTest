from typing import Dict

def get_config() -> Dict:
    return {
        'platformName': 'Android',  # 平台名称：Android/iOS
        'automationName': 'UiAutomator2',  # Android自动化引擎
        'deviceName': 'Android Emulator',  # 设备名称
        'noReset': True,  # 不重置应用状态
        'newCommandTimeout': 6000,  # 命令超时时间
        'systemPort': 8200,  # 系统端口
        'autoGrantPermissions': True,  # 自动授予权限
        'unicodeKeyboard': True,  # 使用Unicode输入法
        'resetKeyboard': True,  # 重置输入法
        'noSign': True,  # 不重签名
        'recreateChromeDriverSessions': True,  # 重新创建ChromeDriver会话
        'ensureWebviewsHavePages': True,  # 确保Webview加载完成
        'nativeWebScreenshot': True,  # 使用原生截图
        'waitForIdleTimeout': 0  # 等待空闲超时
    } 