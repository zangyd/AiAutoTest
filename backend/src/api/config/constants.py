"""
常量定义模块

定义应用程序使用的所有常量
"""
from enum import Enum


class UserStatus(str, Enum):
    """用户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class UserRole(str, Enum):
    """用户角色"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class ProjectStatus(str, Enum):
    """项目状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class TestStatus(str, Enum):
    """测试状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestPriority(str, Enum):
    """测试优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestType(str, Enum):
    """测试类型"""
    UNIT = "unit"
    INTEGRATION = "integration"
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"


# 分页默认值
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# 缓存过期时间（秒）
TOKEN_EXPIRE = 60 * 30  # 30分钟
VERIFY_CODE_EXPIRE = 60 * 5  # 5分钟
USER_CACHE_EXPIRE = 60 * 60  # 1小时
PROJECT_CACHE_EXPIRE = 60 * 60 * 24  # 24小时

# 文件相关
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}
ALLOWED_DOC_TYPES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 请求限制
RATE_LIMIT_REQUESTS = 100  # 请求次数
RATE_LIMIT_PERIOD = 60  # 时间窗口（秒）

# 响应码
class ResponseCode:
    """响应码定义"""
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    VALIDATION_ERROR = 422
    INTERNAL_ERROR = 500 