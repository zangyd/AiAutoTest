"""令牌黑名单测试"""
import pytest
import jwt
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from core.auth.token_blacklist import TokenBlacklist
from core.config.settings import settings

# 标记使用asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_redis():
    """模拟Redis客户端"""
    redis_mock = AsyncMock()
    
    # 模拟Redis方法
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = True
    redis_mock.exists.return_value = False
    
    return redis_mock

@pytest.fixture
def token_blacklist(mock_redis):
    """创建令牌黑名单实例"""
    return TokenBlacklist(mock_redis)

@pytest.fixture
def test_token():
    """创建测试令牌"""
    payload = {
        "sub": "1",
        "username": "testuser",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

class TestTokenBlacklist:
    """令牌黑名单测试类"""
    
    async def test_add_to_blacklist(self, token_blacklist, test_token, mock_redis):
        """测试将令牌添加到黑名单"""
        # 将令牌添加到黑名单
        result = await token_blacklist.add_to_blacklist(test_token)
        
        # 断言
        assert result is True
        mock_redis.set.assert_called_once()
    
    async def test_is_blacklisted(self, token_blacklist, test_token, mock_redis):
        """测试检查令牌是否在黑名单中"""
        # 设置模拟返回值
        mock_redis.exists.return_value = True
        
        # 检查令牌是否在黑名单中
        result = await token_blacklist.is_blacklisted(test_token)
        
        # 断言
        assert result is True
        mock_redis.exists.assert_called_once()
    
    async def test_is_not_blacklisted(self, token_blacklist, test_token, mock_redis):
        """测试检查令牌不在黑名单中"""
        # 设置模拟返回值
        mock_redis.exists.return_value = False
        
        # 检查令牌是否在黑名单中
        result = await token_blacklist.is_blacklisted(test_token)
        
        # 断言
        assert result is False
        mock_redis.exists.assert_called_once()
    
    async def test_add_to_blacklist_invalid_token(self, token_blacklist, mock_redis):
        """测试将无效令牌添加到黑名单"""
        # 将无效令牌添加到黑名单
        result = await token_blacklist.add_to_blacklist("invalid_token")
        
        # 断言
        assert result is False
        mock_redis.set.assert_not_called()
    
    async def test_is_blacklisted_invalid_token(self, token_blacklist, mock_redis):
        """测试检查无效令牌是否在黑名单中"""
        # 设置模拟返回值
        mock_redis.exists.return_value = False
        
        # 检查无效令牌是否在黑名单中
        result = await token_blacklist.is_blacklisted("invalid_token")
        
        # 断言
        assert result is False
        mock_redis.exists.assert_called_once_with("invalid_token") 