"""
测试辅助工具类
"""
import os
import json
from typing import Any, Dict
from datetime import datetime

class TestHelper:
    @staticmethod
    def load_test_data(file_path: str) -> Dict[str, Any]:
        """
        加载测试数据
        :param file_path: 数据文件路径
        :return: 测试数据字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load test data from {file_path}: {e}")

    @staticmethod
    def save_test_result(result: Dict[str, Any], file_name: str = None):
        """
        保存测试结果
        :param result: 测试结果数据
        :param file_name: 文件名，默认使用时间戳
        """
        if not file_name:
            file_name = f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        result_dir = "test_results"
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
            
        file_path = os.path.join(result_dir, file_name)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save test result to {file_path}: {e}")

    @staticmethod
    def generate_test_data(data_type: str, **kwargs) -> Dict[str, Any]:
        """
        生成测试数据
        :param data_type: 数据类型
        :param kwargs: 其他参数
        :return: 生成的测试数据
        """
        if data_type == "user":
            return {
                "username": kwargs.get("username", "testuser"),
                "password": kwargs.get("password", "password123"),
                "email": kwargs.get("email", "test@example.com")
            }
        elif data_type == "project":
            return {
                "name": kwargs.get("name", "Test Project"),
                "description": kwargs.get("description", "Test Description"),
                "type": kwargs.get("type", "Web")
            }
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

    @staticmethod
    def compare_results(expected: Dict[str, Any], actual: Dict[str, Any]) -> Dict[str, Any]:
        """
        比较预期结果和实际结果
        :param expected: 预期结果
        :param actual: 实际结果
        :return: 比较结果
        """
        differences = {}
        for key in expected:
            if key not in actual:
                differences[key] = {"expected": expected[key], "actual": "Missing"}
            elif expected[key] != actual[key]:
                differences[key] = {"expected": expected[key], "actual": actual[key]}
        
        for key in actual:
            if key not in expected:
                differences[key] = {"expected": "Not Expected", "actual": actual[key]}
                
        return differences 