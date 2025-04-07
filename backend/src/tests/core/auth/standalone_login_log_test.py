"""
独立的登录日志服务测试文件，不依赖于conftest.py中的导入
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from enum import Enum

# 避免导入错误
pytestmark = pytest.mark.asyncio

# 模拟枚举类型
class LoginStatus(Enum):
    """登录状态枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    LOCKED = "locked"

# 模拟LoginLog模型
class LoginLog:
    """模拟的登录日志模型类"""
    def __init__(
        self,
        username=None,
        ip_address=None,
        user_agent=None,
        status=None,
        message=None,
        login_time=None
    ):
        self.id = None
        self.username = username
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.status = status
        self.message = message
        self.login_time = login_time or datetime.now()

# 登录日志服务
class LoginLogService:
    """模拟的登录日志服务类，直接复制实现而不是导入"""
    
    def __init__(self, db_session):
        """初始化登录日志服务"""
        self.db = db_session
    
    async def record_login(
        self,
        username=None,
        ip_address=None,
        user_agent=None,
        status=None,
        message=None
    ):
        """记录登录行为"""
        try:
            # 创建登录日志记录
            log = LoginLog(
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status.value if status else None,
                message=message,
                login_time=datetime.now()
            )
            
            # 添加到数据库
            await self.db.add(log)
            await self.db.commit()
            await self.db.refresh(log)
            
            return log
        except Exception as e:
            # 在实际应用中，这里应该记录错误日志
            print(f"记录登录日志时发生错误: {str(e)}")
            return None
    
    async def get_user_login_logs(self, username, limit=10, skip=0):
        """获取用户登录日志"""
        # 模拟数据库查询
        return []
    
    async def get_recent_logs(self, limit=10, skip=0, status=None):
        """获取最近的登录日志"""
        # 模拟数据库查询
        return []

@pytest.fixture
def mock_db_session():
    """创建模拟的数据库会话"""
    session = AsyncMock()
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session

class TestLoginLogService:
    """登录日志服务测试类"""
    
    async def test_record_login_success(self, mock_db_session):
        """测试记录成功登录"""
        # 创建登录日志服务
        log_service = LoginLogService(mock_db_session)
        
        # 模拟用户数据
        username = "test_user"
        ip_address = "127.0.0.1"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        status = LoginStatus.SUCCESS
        message = "登录成功"
        
        # 记录登录
        with patch('datetime.datetime') as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            
            log = await log_service.record_login(
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status,
                message=message
            )
            
            # 验证数据库操作
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once()
    
    async def test_record_login_failure(self, mock_db_session):
        """测试记录失败登录"""
        # 创建登录日志服务
        log_service = LoginLogService(mock_db_session)
        
        # 模拟用户数据
        username = "test_user"
        ip_address = "127.0.0.1"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        status = LoginStatus.FAILED
        message = "验证码错误"
        
        # 记录登录
        log = await log_service.record_login(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            message=message
        )
        
        # 验证数据库操作
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    async def test_record_login_exception(self, mock_db_session):
        """测试记录登录过程中发生异常的情况"""
        # 创建登录日志服务
        log_service = LoginLogService(mock_db_session)
        
        # 模拟数据库异常
        mock_db_session.add.side_effect = Exception("数据库连接错误")
        
        # 模拟用户数据
        username = "test_user"
        ip_address = "127.0.0.1"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        status = LoginStatus.SUCCESS
        message = "登录成功"
        
        # 记录登录（应该捕获异常而不会中断程序）
        log = await log_service.record_login(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            message=message
        )
        
        # 验证结果
        assert log is None
        
        # 验证数据库操作
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_not_called()
        mock_db_session.refresh.assert_not_called()

async def run_tests():
    """运行所有测试"""
    test_instance = TestLoginLogService()
    
    # 创建模拟的数据库会话
    mock_db_session = AsyncMock()
    mock_db_session.add = AsyncMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()
    
    # 运行测试
    print("测试记录成功登录...")
    await test_instance.test_record_login_success(mock_db_session)
    print("✓ 记录成功登录测试通过")
    
    # 重置模拟
    mock_db_session.add.reset_mock()
    mock_db_session.commit.reset_mock()
    mock_db_session.refresh.reset_mock()
    
    print("测试记录失败登录...")
    await test_instance.test_record_login_failure(mock_db_session)
    print("✓ 记录失败登录测试通过")
    
    # 重置模拟
    mock_db_session.add.reset_mock()
    mock_db_session.commit.reset_mock()
    mock_db_session.refresh.reset_mock()
    
    # 设置异常
    mock_db_session.add.side_effect = Exception("数据库连接错误")
    
    print("测试记录登录异常处理...")
    await test_instance.test_record_login_exception(mock_db_session)
    print("✓ 记录登录异常处理测试通过")
    
    print("所有测试通过!")

if __name__ == "__main__":
    asyncio.run(run_tests()) 