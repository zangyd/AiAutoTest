import os
import json
from datetime import datetime
from typing import Any, Dict

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
        screenshots_dir = os.path.join('tests', 'e2e', 'reports', 'screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)
        return os.path.join(screenshots_dir, f'{test_name}_{timestamp}.png')
        
    @staticmethod
    def get_video_path(test_name: str) -> str:
        """获取视频保存路径"""
        timestamp = TestUtils.get_timestamp()
        videos_dir = os.path.join('tests', 'e2e', 'reports', 'videos')
        os.makedirs(videos_dir, exist_ok=True)
        return os.path.join(videos_dir, f'{test_name}_{timestamp}.webm')
        
    @staticmethod
    def get_trace_path(test_name: str) -> str:
        """获取跟踪文件保存路径"""
        timestamp = TestUtils.get_timestamp()
        traces_dir = os.path.join('tests', 'e2e', 'reports', 'traces')
        os.makedirs(traces_dir, exist_ok=True)
        return os.path.join(traces_dir, f'{test_name}_{timestamp}.zip') 