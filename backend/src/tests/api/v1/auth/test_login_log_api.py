"""
登录日志API测试模块
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from fastapi import status
from datetime import datetime, timedelta

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_login_log_service():
    """创建模拟的登录日志服务"""
    mock = AsyncMock()
    mock.record_login.return_value = None
    return mock


@pytest.fixture
def mock_app(app, mock_login_log_service):
    """为测试准备模拟的应用"""
    # 模拟应用的依赖项
    app.dependency_overrides = {
        # 这里可以添加更多的依赖项覆盖
    }
    # 将模拟的登录日志服务添加到应用状态
    app.state.login_log_service = mock_login_log_service
    return app


@pytest.fixture
def mock_login_log_models():
    """模拟登录日志模型数据"""
    now = datetime.now()
    return [
        {
            "id": 1,
            "username": "user1",
            "ip_address": "192.168.1.1",
            "user_agent": "Chrome",
            "status": "success",
            "message": "登录成功",
            "login_time": (now - timedelta(minutes=5)).isoformat()
        },
        {
            "id": 2,
            "username": "user2",
            "ip_address": "192.168.1.2", 
            "user_agent": "Firefox",
            "status": "failed",
            "message": "密码错误",
            "login_time": (now - timedelta(minutes=10)).isoformat()
        },
        {
            "id": 3,
            "username": "user1",
            "ip_address": "192.168.1.3",
            "user_agent": "Mobile",
            "status": "failed",
            "message": "验证码错误",
            "login_time": (now - timedelta(minutes=15)).isoformat()
        }
    ]


class TestLoginLogAPI:
    """登录日志API测试类"""
    
    async def test_login_with_logging(self, async_client, mock_app, mock_authenticate_user, mock_login_log_service):
        """测试登录过程中的日志记录"""
        # 登录数据
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        
        # 发送请求
        response = await async_client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers={
                "User-Agent": "TestAgent",
                "X-Forwarded-For": "192.168.1.100"
            }
        )
        
        # 检查响应状态
        assert response.status_code == status.HTTP_200_OK
        
        # 检查登录日志服务是否被调用
        mock_login_log_service.record_login.assert_called_once()
        
        # 验证记录的参数
        call_args = mock_login_log_service.record_login.call_args[1]
        assert call_args["username"] == "testuser"
        assert call_args["ip_address"] == "192.168.1.100"
        assert call_args["user_agent"] == "TestAgent"
    
    async def test_login_failure_with_logging(self, async_client, mock_app, mock_login_log_service):
        """测试登录失败时的日志记录"""
        # 设置认证失败
        with patch("core.auth.service.AuthService.authenticate_user", side_effect=Exception("认证失败")):
            # 登录数据
            login_data = {
                "username": "testuser",
                "password": "wrong_password"
            }
            
            # 发送请求
            response = await async_client.post(
                "/api/v1/auth/login",
                json=login_data,
                headers={
                    "User-Agent": "TestAgent",
                    "X-Forwarded-For": "192.168.1.100"
                }
            )
            
            # 检查响应状态应该是错误
            assert response.status_code != status.HTTP_200_OK
            
            # 检查登录日志服务是否被调用（失败也应该记录）
            mock_login_log_service.record_login.assert_called_once()
            
            # 验证记录的参数
            call_args = mock_login_log_service.record_login.call_args[1]
            assert call_args["username"] == "testuser"
            assert call_args["status"].value == "failed"  # 使用枚举值而不是字符串
    
    @patch("sqlalchemy.ext.asyncio.AsyncSession.execute")
    @patch("sqlalchemy.future.select")
    async def test_get_login_logs(self, mock_select, mock_execute, async_client, mock_app, user_token, mock_login_log_models):
        """测试获取登录日志列表"""
        # 设置模拟返回值
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_login_log_models
        mock_execute.return_value = mock_result
        
        # 发送请求
        response = await async_client.get(
            "/api/v1/auth/logs",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # 检查响应状态
        assert response.status_code == status.HTTP_200_OK
        
        # 检查响应内容
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["username"] == "user1"
        assert data[1]["username"] == "user2"
        assert data[2]["username"] == "user1"
    
    @patch("sqlalchemy.ext.asyncio.AsyncSession.execute")
    @patch("sqlalchemy.future.select")
    async def test_get_login_logs_with_filters(self, mock_select, mock_execute, async_client, mock_app, user_token, mock_login_log_models):
        """测试带过滤条件获取登录日志"""
        # 设置模拟返回值 - 只返回用户user1的日志
        filtered_logs = [log for log in mock_login_log_models if log["username"] == "user1"]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = filtered_logs
        mock_execute.return_value = mock_result
        
        # 发送请求 - 带用户名过滤
        response = await async_client.get(
            "/api/v1/auth/logs?username=user1",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # 检查响应状态
        assert response.status_code == status.HTTP_200_OK
        
        # 检查响应内容 - 只应有用户user1的日志
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert all(log["username"] == "user1" for log in data)
    
    async def test_get_login_logs_unauthorized(self, async_client, mock_app):
        """测试未授权获取登录日志"""
        # 发送请求 - 不带授权令牌
        response = await async_client.get("/api/v1/auth/logs")
        
        # 检查响应状态 - 应该是未授权
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 