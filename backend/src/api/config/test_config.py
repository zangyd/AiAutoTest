"""
测试配置模块

管理所有测试相关的配置项，包括测试执行、数据、环境等配置
"""
from typing import Dict, List
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from core.config.base_settings import BaseAppSettings

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

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
    
    model_config = ConfigDict(
        env_file=[
            str(ROOT_DIR / ".env"),
            str(ROOT_DIR / ".env.test")
        ],
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_prefix="TEST_EXECUTION__",
        env_nested_delimiter="__",
        extra="allow",
        title="测试执行配置"
    )

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
    
    model_config = ConfigDict(
        env_file=[
            str(ROOT_DIR / ".env"),
            str(ROOT_DIR / ".env.test")
        ],
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_prefix="TEST_DATA__",
        env_nested_delimiter="__",
        extra="allow",
        title="测试数据配置"
    )

class TestSettings(BaseAppSettings):
    """测试配置类"""
    
    # 测试执行配置
    TEST_PARALLEL: bool = Field(default=True, description="是否启用并行测试")
    TEST_WORKERS: int = Field(default=4, description="并行测试工作进程数")
    TEST_TIMEOUT: int = Field(default=300, description="测试超时时间(秒)")
    TEST_RETRIES: int = Field(default=2, description="测试重试次数")
    
    # 测试数据配置
    TEST_DATA_PATH: str = Field(default="tests/data", description="测试数据目录")
    TEST_TEMP_PATH: str = Field(default="tests/temp", description="测试临时文件目录")
    TEST_CLEAN_TEMP: bool = Field(default=True, description="是否清理临时文件")
    
    # 测试报告配置
    TEST_REPORT_PATH: str = Field(default="tests/reports", description="测试报告目录")
    TEST_REPORT_FORMAT: str = Field(default="html", description="测试报告格式")
    TEST_REPORT_TITLE: str = Field(default="AutoTest Report", description="测试报告标题")
    
    # UI测试配置
    TEST_BROWSER: str = Field(default="chrome", description="测试浏览器")
    TEST_HEADLESS: bool = Field(default=True, description="是否使用无头模式")
    TEST_WINDOW_WIDTH: int = Field(default=1920, description="浏览器窗口宽度")
    TEST_WINDOW_HEIGHT: int = Field(default=1080, description="浏览器窗口高度")
    TEST_SCREENSHOT_PATH: str = Field(default="tests/screenshots", description="截图保存目录")
    
    # API测试配置
    TEST_API_HOST: str = Field(default="localhost", description="API测试主机")
    TEST_API_PORT: int = Field(default=8000, description="API测试端口")
    TEST_API_PROTOCOL: str = Field(default="http", description="API测试协议")
    TEST_API_VERSION: str = Field(default="v1", description="API版本")
    TEST_API_TIMEOUT: int = Field(default=30, description="API请求超时时间")
    TEST_API_MAX_RETRIES: int = Field(default=3, description="API请求重试次数")
    
    # 移动端测试配置
    TEST_MOBILE_PLATFORM: str = Field(default="android", description="移动测试平台")
    TEST_DEVICE_NAME: str = Field(default="emulator-5554", description="测试设备名称")
    TEST_APP_PATH: str = Field(default="tests/apps", description="测试应用目录")
    TEST_APP_PACKAGE: str = Field(default="com.example.app", description="测试应用包名")
    
    # Mock服务配置
    TEST_MOCK_ENABLED: bool = Field(default=True, description="是否启用Mock服务")
    TEST_MOCK_PORT: int = Field(default=8001, description="Mock服务端口")
    TEST_MOCK_DATA_PATH: str = Field(default="tests/mock", description="Mock数据目录")
    
    # 性能测试配置
    TEST_PERF_USERS: int = Field(default=100, description="并发用户数")
    TEST_PERF_RAMP_UP: int = Field(default=30, description="加压时间(秒)")
    TEST_PERF_DURATION: int = Field(default=300, description="持续时间(秒)")
    TEST_PERF_REPORT_PATH: str = Field(default="tests/performance", description="性能测试报告目录")
    
    model_config = ConfigDict(
        env_prefix="TEST_"  # 使用TEST_前缀区分配置
    )
    
    @property
    def api_base_url(self) -> str:
        """获取API基础URL"""
        return f"{self.TEST_API_PROTOCOL}://{self.TEST_API_HOST}:{self.TEST_API_PORT}/api/{self.TEST_API_VERSION}"
    
    @property
    def mobile_capabilities(self) -> dict:
        """获取移动端测试配置"""
        return {
            "platformName": self.TEST_MOBILE_PLATFORM,
            "deviceName": self.TEST_DEVICE_NAME,
            "app": f"{self.TEST_APP_PATH}/{self.TEST_APP_PACKAGE}.apk"
        }
    
    def _configure_for_environment(self) -> None:
        """根据环境配置特定的设置"""
        super()._configure_for_environment()
        
        if self.ENV == "test":
            # 测试环境使用更小的配置
            self.TEST_WORKERS = 2
            self.TEST_TIMEOUT = 60
            self.TEST_PERF_USERS = 10
            self.TEST_PERF_DURATION = 60
            self.TEST_API_TIMEOUT = 5
        elif self.ENV == "production":
            # 生产环境使用更严格的配置
            self.TEST_PARALLEL = False
            self.TEST_HEADLESS = True
            self.TEST_CLEAN_TEMP = True
            self.TEST_API_MAX_RETRIES = 5

# 导出配置实例
test_execution_config = TestExecutionConfig()
test_framework_config = TestFrameworkConfig()
test_data_config = TestDataConfig()

# 创建全局测试配置实例
test_settings = TestSettings() 