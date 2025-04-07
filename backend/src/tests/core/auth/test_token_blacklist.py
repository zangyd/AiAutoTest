"""令牌黑名单测试"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import jwt
import time
from datetime import datetime, timedelta

from core.auth.token_blacklist import TokenBlacklist
from core.config.settings import settings

# 标记使用asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_redis():
    """创建一个模拟的Redis客户端"""
    redis = AsyncMock()
    
    # 模拟缓存管理器方法
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    redis.exists = AsyncMock(return_value=False)
    
    return redis

@pytest.fixture
def token_blacklist(mock_redis):
    """创建一个TokenBlacklist实例用于测试"""
    return TokenBlacklist(redis=mock_redis)

@pytest.fixture
def mock_jwt_decode():
    """模拟jwt.decode函数"""
    with patch('jwt.decode') as mock:
        mock.return_value = {
            'sub': '1',
            'username': 'testuser',
            'exp': int(time.time()) + 3600  # 1小时后过期
        }
        yield mock

@pytest.fixture
def mock_jwt_decode_expired():
    """模拟jwt.decode函数返回已过期的token"""
    with patch('jwt.decode') as mock:
        mock.return_value = {
            'sub': '1',
            'username': 'testuser',
            'exp': int(time.time()) - 3600  # 1小时前过期
        }
        yield mock

@pytest.fixture
def mock_cache_manager():
    """模拟CacheManager"""
    with patch('core.cache.cache_manager.CacheManager') as mock:
        instance = MagicMock()
        
        # 模拟缓存管理器方法
        instance.get = AsyncMock(return_value=None)
        instance.set = AsyncMock(return_value=True)
        instance.delete = AsyncMock(return_value=True)
        instance.exists = AsyncMock(return_value=False)
        
        mock.return_value = instance
        yield instance

class TestTokenBlacklist:
    """令牌黑名单测试类"""
    
    @pytest.mark.asyncio
    async def test_add_to_blacklist(self, token_blacklist, mock_jwt_decode, mock_cache_manager):
        """测试将令牌添加到黑名单"""
        # 准备测试数据
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJ0ZXN0dXNlciJ9.signature"
        
        # 设置模拟行为
        mock_cache_manager.set.return_value = True
        
        # 测试添加到黑名单
        result = await token_blacklist.add_to_blacklist(token)
        
        # 断言结果
        assert result is True
        mock_cache_manager.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_to_blacklist_expired_token(self, token_blacklist, mock_jwt_decode_expired, mock_cache_manager):
        """测试将已过期的令牌添加到黑名单"""
        # 准备测试数据
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJ0ZXN0dXNlciJ9.signature"
        
        # 设置模拟行为
        mock_cache_manager.set.return_value = True
        
        # 测试添加到黑名单
        result = await token_blacklist.add_to_blacklist(token)
        
        # 断言结果
        assert result is True
        mock_cache_manager.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_to_blacklist_invalid_token(self, token_blacklist, mock_cache_manager):
        """测试将无效的令牌添加到黑名单"""
        # 准备测试数据
        token = "invalid_token"
        
        # 设置模拟行为 - jwt.decode会抛出异常
        with patch('jwt.decode', side_effect=jwt.InvalidTokenError("Invalid token")):
            # 测试添加到黑名单
            result = await token_blacklist.add_to_blacklist(token)
        
        # 断言结果
        assert result is False
        mock_cache_manager.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_is_blacklisted_true(self, token_blacklist, mock_jwt_decode, mock_cache_manager):
        """测试检查令牌是否在黑名单中 - 是"""
        # 准备测试数据
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJ0ZXN0dXNlciJ9.signature"
        
        # 设置模拟行为
        mock_cache_manager.exists.return_value = True
        
        # 测试检查是否在黑名单中
        result = await token_blacklist.is_blacklisted(token)
        
        # 断言结果
        assert result is True
        mock_cache_manager.exists.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_is_blacklisted_false(self, token_blacklist, mock_jwt_decode, mock_cache_manager):
        """测试检查令牌是否在黑名单中 - 否"""
        # 准备测试数据
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJ0ZXN0dXNlciJ9.signature"
        
        # 设置模拟行为
        mock_cache_manager.exists.return_value = False
        
        # 测试检查是否在黑名单中
        result = await token_blacklist.is_blacklisted(token)
        
        # 断言结果
        assert result is False
        mock_cache_manager.exists.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_is_blacklisted_invalid_token(self, token_blacklist, mock_cache_manager):
        """测试检查无效令牌是否在黑名单中"""
        # 准备测试数据
        token = "invalid_token"
        
        # 设置模拟行为 - jwt.decode会抛出异常
        with patch('jwt.decode', side_effect=jwt.InvalidTokenError("Invalid token")):
            # 设置额外的模拟行为
            mock_cache_manager.exists.return_value = False
            
            # 测试检查是否在黑名单中
            result = await token_blacklist.is_blacklisted(token)
        
        # 断言结果 - 应该尝试直接使用token作为键
        assert result is False
        mock_cache_manager.exists.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_expired(self, token_blacklist):
        """测试清理过期的黑名单记录"""
        # 测试清理过期记录
        result = await token_blacklist.clear_expired()
        
        # 断言结果 - 目前这是一个空方法，返回0
        assert result == 0 