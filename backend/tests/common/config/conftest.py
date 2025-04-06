import os
import pytest
from datetime import datetime
from ...mobile.config.mobile_config import TEST_CONFIG

def pytest_configure(config):
    """
    pytest配置
    """
    # 创建截图和视频目录
    for dir_name in [TEST_CONFIG['screenshot_dir'], TEST_CONFIG['video_dir']]:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

@pytest.fixture(scope="function", autouse=True)
def test_log(request):
    """
    测试日志装饰器
    """
    test_name = request.node.name
    print(f"\n开始测试: {test_name} at {datetime.now()}")
    yield
    print(f"\n结束测试: {test_name} at {datetime.now()}")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试报告钩子
    """
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        if report.failed:
            print(f"\n测试失败: {item.name}")
            print(f"失败原因: {call.excinfo}")
        else:
            print(f"\n测试通过: {item.name}")

def pytest_addoption(parser):
    """
    添加命令行选项
    """
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        help="指定测试平台: android 或 ios"
    )
    parser.addoption(
        "--device",
        action="store",
        help="指定设备名称"
    )

@pytest.fixture(scope="session")
def platform(request):
    """
    获取测试平台
    """
    return request.config.getoption("--platform")

@pytest.fixture(scope="session")
def device(request):
    """
    获取设备名称
    """
    return request.config.getoption("--device") 