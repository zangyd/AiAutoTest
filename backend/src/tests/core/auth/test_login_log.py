"""
登录日志功能的单元测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from core.auth.login_log import LoginLogService
from models.auth import LoginLog, LoginStatus

pytestmark = pytest.mark.asyncio


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
        with patch('core.auth.login_log.datetime') as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            
            await log_service.record_login(
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
            
            # 验证添加到数据库的对象
            log_entry = mock_db_session.add.call_args[0][0]
            assert isinstance(log_entry, LoginLog)
            assert log_entry.username == username
            assert log_entry.ip_address == ip_address
            assert log_entry.user_agent == user_agent
            assert log_entry.status == status.value
            assert log_entry.message == message
            assert log_entry.login_time == mock_now
    
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
        await log_service.record_login(
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
        
        # 验证添加到数据库的对象
        log_entry = mock_db_session.add.call_args[0][0]
        assert isinstance(log_entry, LoginLog)
        assert log_entry.username == username
        assert log_entry.ip_address == ip_address
        assert log_entry.user_agent == user_agent
        assert log_entry.status == status.value
        assert log_entry.message == message
    
    async def test_record_login_captcha_failure(self, mock_db_session):
        """测试记录验证码错误的登录尝试"""
        # 创建登录日志服务
        log_service = LoginLogService(mock_db_session)
        
        # 模拟用户数据
        username = "test_user"
        ip_address = "127.0.0.1"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        status = LoginStatus.FAILED
        message = "验证码验证失败"
        
        # 记录登录
        await log_service.record_login(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            message=message
        )
        
        # 验证数据库操作
        mock_db_session.add.assert_called_once()
        
        # 验证添加到数据库的对象
        log_entry = mock_db_session.add.call_args[0][0]
        assert log_entry.status == LoginStatus.FAILED.value
        assert log_entry.message == "验证码验证失败"
    
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
        try:
            await log_service.record_login(
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status,
                message=message
            )
            # 如果没有抛出异常，测试通过
            assert True
        except Exception:
            # 如果抛出异常，测试失败
            pytest.fail("LoginLogService.record_login 未正确处理异常")
        
        # 验证数据库操作
        mock_db_session.add.assert_called_once()
        # 由于异常，commit和refresh应该没有被调用
        mock_db_session.commit.assert_not_called()
        mock_db_session.refresh.assert_not_called()
    
    async def test_record_login_missing_fields(self, mock_db_session):
        """测试记录登录时缺少字段的情况"""
        # 创建登录日志服务
        log_service = LoginLogService(mock_db_session)
        
        # 调用服务方法，省略某些可选参数
        await log_service.record_login(
            username="test_user",
            ip_address=None,  # 缺少IP地址
            user_agent=None,  # 缺少User Agent
            status=LoginStatus.SUCCESS,
            message="登录成功"
        )
        
        # 验证数据库操作
        mock_db_session.add.assert_called_once()
        
        # 验证添加到数据库的对象
        log_entry = mock_db_session.add.call_args[0][0]
        assert log_entry.username == "test_user"
        assert log_entry.ip_address is None  # 应为None
        assert log_entry.user_agent is None  # 应为None 