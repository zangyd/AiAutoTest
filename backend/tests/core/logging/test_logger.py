"""
日志记录组件单元测试
"""
import os
import io
import pytest
import logging
import stat
import threading
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.logging.logger import Logger, AsyncHandler
import json
import sys
from io import StringIO

@pytest.fixture
def temp_log_dir(tmp_path):
    """创建临时日志目录"""
    return tmp_path

@pytest.fixture
def logger_instance(temp_log_dir):
    """创建Logger实例"""
    logger = Logger(
        name="test",
        log_dir=str(temp_log_dir),
        level=logging.DEBUG,
        console_output=False
    )
    yield logger
    logger.close()

def test_logger_initialization(temp_log_dir):
    """测试日志记录器初始化"""
    logger = Logger(
        name="test",
        log_dir=str(temp_log_dir),
        console_output=False
    )
    
    try:
        # 验证日志目录创建
        assert Path(temp_log_dir).exists()
        assert Path(temp_log_dir).is_dir()
        
        # 验证日志文件创建
        log_file = Path(temp_log_dir) / "test.log"
        assert log_file.exists()
        assert log_file.is_file()
    finally:
        logger.close()

def test_log_levels(logger_instance, temp_log_dir):
    """测试不同日志级别"""
    log_file = Path(temp_log_dir) / "test.log"
    
    # 记录不同级别的日志
    logger_instance.debug("Debug message")
    logger_instance.info("Info message")
    logger_instance.warning("Warning message")
    logger_instance.error("Error message")
    logger_instance.critical("Critical message")
    
    # 验证日志文件内容
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Debug message" in content
        assert "Info message" in content
        assert "Warning message" in content
        assert "Error message" in content
        assert "Critical message" in content

def test_log_with_context(logger_instance, temp_log_dir):
    """测试带上下文的日志记录"""
    log_file = Path(temp_log_dir) / "test.log"
    
    # 记录带上下文的日志
    context = {
        "user_id": 123,
        "action": "login",
        "ip": "127.0.0.1"
    }
    logger_instance.info_with_context("User action", context)
    
    # 验证日志文件内容
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "User action" in content
        assert "123" in content
        assert "login" in content
        assert "127.0.0.1" in content

def test_performance_logging(logger_instance, temp_log_dir):
    """测试性能日志记录"""
    log_file = Path(temp_log_dir) / "test.log"
    
    # 使用性能日志记录器
    with logger_instance.log_performance("test_operation"):
        # 模拟一些操作
        _ = [i * 2 for i in range(1000)]
    
    # 验证日志文件内容
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "test_operation" in content
        assert "耗时" in content
        assert "ms" in content

def test_invalid_log_dir():
    """测试无效的日志目录"""
    # 尝试在只读文件系统中创建目录
    with patch('pathlib.Path.mkdir') as mock_mkdir:
        mock_mkdir.side_effect = PermissionError("权限不足")
        with pytest.raises(OSError):
            Logger(
                name="test",
                log_dir="/root/invalid/path",
                console_output=False
            )

def test_log_rotation(temp_log_dir):
    """测试日志轮转"""
    logger = Logger(
        name="test",
        log_dir=str(temp_log_dir),
        max_bytes=100,  # 设置较小的文件大小以触发轮转
        backup_count=2,
        console_output=False
    )
    
    try:
        # 写入足够多的日志以触发轮转
        for i in range(100):
            logger.info(f"Test message {i}")
        
        # 验证轮转文件的创建
        log_files = list(Path(temp_log_dir).glob("test.log*"))
        assert len(log_files) > 1  # 至少有一个轮转文件
    finally:
        logger.close()

def test_error_handling(temp_log_dir):
    """测试错误处理"""
    # 创建一个无权限访问的目录
    no_access_dir = temp_log_dir / "no_access"
    no_access_dir.mkdir()
    
    # 移除所有权限
    current_mode = os.stat(str(no_access_dir)).st_mode
    os.chmod(str(no_access_dir), current_mode & ~(stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO))
    
    try:
        with pytest.raises(OSError, match=r"日志目录无写入权限"):
            Logger(
                name="error_test",
                log_dir=str(no_access_dir)
            )
    finally:
        # 恢复权限以便清理
        os.chmod(str(no_access_dir), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

def test_log_formatting(logger_instance, temp_log_dir):
    """测试日志格式化"""
    log_file = Path(temp_log_dir) / "test.log"
    
    # 记录包含特殊格式的日志
    test_message = "Test message with timestamp"
    logger_instance.info(test_message)
    
    # 验证日志格式
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
        log_data = json.loads(content)
        
        # 验证JSON格式
        assert isinstance(log_data, dict)
        assert "timestamp" in log_data
        assert "level" in log_data
        assert "message" in log_data
        assert "user_id" in log_data
        
        # 验证字段值
        assert log_data["level"] == "INFO"
        assert log_data["message"] == test_message
        assert log_data["user_id"] is None

def test_multiline_logging(logger_instance, temp_log_dir):
    """测试多行日志记录"""
    log_file = Path(temp_log_dir) / "test.log"
    
    # 记录多行日志
    multiline_msg = """Line 1
    Line 2
    Line 3"""
    logger_instance.info(multiline_msg)
    
    # 验证日志内容
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Line 1" in content
        assert "Line 2" in content
        assert "Line 3" in content

def test_concurrent_logging(temp_log_dir):
    """测试并发日志记录"""
    logger = Logger(
        name="test",
        log_dir=str(temp_log_dir),
        console_output=False
    )
    
    try:
        log_file = Path(temp_log_dir) / "test.log"
        
        def log_messages():
            for i in range(100):
                logger.info(f"Thread message {i}")
        
        # 创建多个线程并发记录日志
        threads = [
            threading.Thread(target=log_messages)
            for _ in range(5)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 验证日志文件内容
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
            for i in range(100):
                assert f"Thread message {i}" in content
    finally:
        logger.close()

def test_log_filter(temp_log_dir):
    """测试日志过滤功能"""
    class TestFilter(logging.Filter):
        def filter(self, record):
            return "allow" in record.getMessage()
    
    logger = Logger(
        name="test",
        log_dir=str(temp_log_dir),
        console_output=False
    )
    
    try:
        logger.add_filter(TestFilter())
        
        # 记录日志
        logger.info("This message should be allowed")
        logger.info("This message should be filtered")
        
        # 验证日志文件内容
        with open(Path(temp_log_dir) / "test.log", "r", encoding="utf-8") as f:
            content = f.read()
            assert "should be allowed" in content
            assert "should be filtered" not in content
    finally:
        logger.close()

def test_console_output(capsys, tmpdir):
    """测试控制台输出"""
    # 创建临时日志目录
    log_dir = str(tmpdir)
    
    # 创建日志记录器
    logger = Logger(
        name="test",
        log_dir=log_dir,
        level=logging.INFO,
        console_output=True,
        console_color=False,
        async_mode=False
    )
    
    # 记录测试消息
    test_message = "测试消息"
    logger.info(test_message)
    
    # 确保刷新所有处理器
    logger.flush()
    
    # 关闭日志记录器
    logger.close()
    
    # 获取捕获的输出
    captured = capsys.readouterr()
    output = captured.out
    
    # 验证输出不为空
    assert output.strip(), "控制台输出为空"
    
    # 验证输出包含预期的消息
    log_data = json.loads(output.strip())
    assert log_data["level"] == "INFO"
    assert log_data["message"] == test_message

def test_async_logging(tmpdir):
    """测试异步日志记录"""
    # 创建临时日志目录
    log_dir = str(tmpdir)
    
    # 创建异步日志记录器
    logger = Logger(
        name="test_async",
        log_dir=log_dir,
        level=logging.INFO,
        console_output=False,
        async_mode=True
    )
    
    # 记录多条测试消息
    for i in range(10):
        logger.info(f"异步消息 {i}")
        time.sleep(0.01)  # 给异步处理一些时间
    
    # 确保刷新所有处理器
    logger.flush()
    time.sleep(0.1)  # 给异步处理一些额外时间
    
    # 关闭日志记录器
    logger.close()
    
    # 验证日志文件存在
    log_file = Path(log_dir) / "test_async.log"
    assert log_file.exists(), "日志文件不存在"
    
    # 读取日志文件内容
    with open(log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()
    
    # 验证日志文件不为空
    assert log_content.strip(), "日志文件为空"
    
    # 验证所有消息都被记录
    log_lines = [line for line in log_content.strip().split('\n') if line.strip()]
    assert len(log_lines) == 10, f"预期10条消息，实际有{len(log_lines)}条"
    
    # 验证每条消息的格式
    for i, line in enumerate(log_lines):
        log_data = json.loads(line)
        assert log_data["level"] == "INFO"
        assert log_data["message"] == f"异步消息 {i}" 