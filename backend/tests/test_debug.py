import pytest
import time
from src.core.debug import debug_tools, debug_decorator, performance_monitor

def test_variable_watch():
    """测试变量监视功能"""
    # 监视变量变化
    debug_tools.watch_variable("test_var", 1)
    debug_tools.watch_variable("test_var", 2)
    
    # 验证变量是否被正确记录
    assert debug_tools.watch_variables["test_var"] == 2

def test_breakpoints():
    """测试断点管理功能"""
    # 设置断点
    debug_tools.set_breakpoint("test.py", 10)
    
    # 验证断点是否被正确设置
    assert ("test.py", 10) in debug_tools.config.BREAKPOINTS
    
    # 移除断点
    debug_tools.remove_breakpoint("test.py", 10)
    
    # 验证断点是否被正确移除
    assert ("test.py", 10) not in debug_tools.config.BREAKPOINTS

@debug_decorator
def sample_function(a: int, b: int) -> int:
    """用于测试的示例函数"""
    time.sleep(0.1)  # 模拟耗时操作
    return a + b

def test_performance_monitor():
    """测试性能监控功能"""
    # 开始监控
    performance_monitor.start_monitor("test_function")
    
    # 执行一些操作
    result = sample_function(1, 2)
    
    # 结束监控
    performance_monitor.end_monitor("test_function")
    
    # 验证结果
    assert result == 3
    assert "test_function" in performance_monitor.function_times

def test_debug_decorator():
    """测试调试装饰器功能"""
    # 调用被装饰的函数
    result = sample_function(3, 4)
    
    # 验证函数执行结果
    assert result == 7

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 