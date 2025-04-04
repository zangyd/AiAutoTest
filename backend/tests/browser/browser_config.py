from typing import Dict, Any
from pathlib import Path

def get_chrome_config() -> Dict[str, Any]:
    """Chrome浏览器配置"""
    return {
        'browserName': 'chrome',
        'goog:chromeOptions': {
            'args': [
                '--start-maximized',  # 最大化窗口
                '--disable-gpu',      # 禁用GPU加速
                '--no-sandbox',       # 禁用沙箱模式
                '--disable-dev-shm-usage',  # 禁用/dev/shm使用
                '--disable-infobars', # 禁用信息栏
                '--disable-notifications',  # 禁用通知
                '--disable-extensions'  # 禁用扩展
            ],
            'excludeSwitches': ['enable-automation'],  # 排除自动化提示
            'prefs': {
                'download.default_directory': str(Path.cwd() / 'downloads'),  # 下载目录
                'download.prompt_for_download': False,  # 禁用下载提示
                'profile.default_content_settings.popups': 0  # 禁用弹窗
            }
        }
    }

def get_firefox_config() -> Dict[str, Any]:
    """Firefox浏览器配置"""
    return {
        'browserName': 'firefox',
        'moz:firefoxOptions': {
            'args': ['-headless'],
            'prefs': {
                'browser.download.folderList': 2,  # 使用自定义下载目录
                'browser.download.dir': str(Path.cwd() / 'downloads'),  # 下载目录
                'browser.download.useDownloadDir': True,  # 使用下载目录
                'browser.helperApps.neverAsk.saveToDisk': 'application/octet-stream'  # 自动下载类型
            }
        }
    }

def get_edge_config() -> Dict[str, Any]:
    """Edge浏览器配置"""
    return {
        'browserName': 'MicrosoftEdge',
        'ms:edgeOptions': {
            'args': [
                '--start-maximized',
                '--disable-gpu',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-infobars'
            ],
            'excludeSwitches': ['enable-automation'],
            'prefs': {
                'download.default_directory': str(Path.cwd() / 'downloads'),
                'download.prompt_for_download': False,
                'profile.default_content_settings.popups': 0
            }
        }
    }

def get_browser_config(browser_name: str = 'chrome') -> Dict[str, Any]:
    """获取指定浏览器的配置"""
    config_map = {
        'chrome': get_chrome_config,
        'firefox': get_firefox_config,
        'edge': get_edge_config
    }
    return config_map.get(browser_name.lower(), get_chrome_config)() 