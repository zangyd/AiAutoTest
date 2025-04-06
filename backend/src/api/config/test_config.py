"""
测试相关配置
"""
from typing import Dict, List
from pydantic import BaseModel, Field, ConfigDict

class TestExecutionConfig(BaseModel):
    """测试执行配置"""
    # 并发配置
    max_workers: int = Field(default=5, description="最大并发执行数")
    timeout: int = Field(default=3600, description="单个测试超时时间(秒)")
    retry_times: int = Field(default=3, description="失败重试次数")
    retry_interval: int = Field(default=5, description="重试间隔时间(秒)")
    
    # 环境配置
    cleanup_on_finish: bool = Field(default=True, description="测试完成后清理环境")
    save_artifacts: bool = Field(default=True, description="保存测试产物")
    artifacts_expire_days: int = Field(default=30, description="测试产物保留天数")
    
    # 报告配置
    report_formats: List[str] = Field(
        default=["html", "json"],
        description="报告格式"
    )
    report_template: str = Field(
        default="default",
        description="报告模板"
    )
    
    model_config = ConfigDict(title="测试执行配置")

class TestFrameworkConfig(BaseModel):
    """测试框架配置"""
    # Pytest配置
    pytest_options: Dict[str, str] = Field(
        default={
            "verbose": "true",
            "capture": "no",
            "log-level": "INFO",
            "log-format": "%(asctime)s %(levelname)s %(message)s",
            "log-date-format": "%Y-%m-%d %H:%M:%S"
        },
        description="Pytest运行选项"
    )
    
    # Playwright配置
    playwright_options: Dict[str, str] = Field(
        default={
            "browser": "chromium",
            "headless": "true",
            "slow_mo": "50",
            "viewport_size": "1920,1080"
        },
        description="Playwright运行选项"
    )
    
    # Appium配置
    appium_options: Dict[str, str] = Field(
        default={
            "platformName": "Android",
            "automationName": "UiAutomator2",
            "noReset": "false",
            "newCommandTimeout": "7200"
        },
        description="Appium运行选项"
    )
    
    model_config = ConfigDict(title="测试框架配置")

class TestDataConfig(BaseModel):
    """测试数据配置"""
    # 数据存储配置
    storage_path: str = Field(
        default="test_data",
        description="测试数据存储路径"
    )
    backup_path: str = Field(
        default="test_data_backup",
        description="测试数据备份路径"
    )
    
    # 数据生成配置
    data_seed: int = Field(
        default=42,
        description="随机数据种子"
    )
    locale: str = Field(
        default="zh_CN",
        description="数据地区设置"
    )
    
    # 数据清理配置
    cleanup_interval: int = Field(
        default=7,
        description="数据清理间隔(天)"
    )
    max_backup_count: int = Field(
        default=5,
        description="最大备份数量"
    )
    
    model_config = ConfigDict(title="测试数据配置")

# 导出配置实例
test_execution_config = TestExecutionConfig()
test_framework_config = TestFrameworkConfig()
test_data_config = TestDataConfig() 