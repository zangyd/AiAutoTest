import os
import json
from datetime import datetime
from typing import Dict, Any

class TestUtils:
    @staticmethod
    def load_test_data(file_path: str) -> Dict[str, Any]:
        """加载测试数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    @staticmethod
    def get_timestamp() -> str:
        """获取当前时间戳"""
        return datetime.now().strftime('%Y%m%d_%H%M%S')
        
    @staticmethod
    def get_screenshot_path(test_name: str) -> str:
        """获取截图保存路径"""
        timestamp = TestUtils.get_timestamp()
        screenshots_dir = os.path.join('tests', 'mobile', 'reports', 'screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)
        return os.path.join(screenshots_dir, f'{test_name}_{timestamp}.png')
        
    @staticmethod
    def get_video_path(test_name: str) -> str:
        """获取录屏保存路径"""
        timestamp = TestUtils.get_timestamp()
        videos_dir = os.path.join('tests', 'mobile', 'reports', 'videos')
        os.makedirs(videos_dir, exist_ok=True)
        return os.path.join(videos_dir, f'{test_name}_{timestamp}.mp4')
        
    @staticmethod
    def get_device_info() -> Dict[str, str]:
        """获取设备信息"""
        return {
            'platformName': os.environ.get('PLATFORM_NAME', 'Android'),
            'deviceName': os.environ.get('DEVICE_NAME', 'Android Emulator'),
            'udid': os.environ.get('DEVICE_UDID', ''),
            'platformVersion': os.environ.get('PLATFORM_VERSION', '')
        } 