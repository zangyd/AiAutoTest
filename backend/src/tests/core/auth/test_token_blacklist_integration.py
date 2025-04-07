"""
令牌黑名单集成测试
此测试验证令牌黑名单与Redis交互以及JWT令牌验证的完整流程
"""
import pytest
import jwt
from datetime import datetime, timedelta
import time
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from core.auth.token_blacklist import TokenBlacklist
from core.cache.redis_manager import get_redis_client
from core.config.settings import settings


pytestmark = pytest.mark.asyncio


@pytest.fixture
async def setup_redis():
    """设置Redis连接并确保测试后清理数据"""
    # 获取真实的Redis客户端
    redis_client = await get_redis_client()
    
    # 创建一个特定前缀用于测试，以避免干扰生产数据
    test_prefix = f"test_blacklist_{int(time.time())}"
    
    # 创建黑名单实例
    token_blacklist = TokenBlacklist(redis_client, key_prefix=test_prefix)
    
    yield token_blacklist
    
    # 清理测试数据
    keys = await redis_client.keys(f"{test_prefix}:*")
    if keys:
        await redis_client.delete(*keys)
    await redis_client.close()


def create_test_token(payload, secret_key=None, algorithm=None):
    """创建测试用的JWT令牌"""
    secret = secret_key or settings.JWT_SECRET_KEY
    alg = algorithm or settings.JWT_ALGORITHM
    return jwt.encode(payload, secret, algorithm=alg)


@pytest.fixture
def valid_token():
    """创建有效的JWT令牌"""
    payload = {
        "sub": "test_user",
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow(),
        "username": "test_user"
    }
    return create_test_token(payload)


@pytest.fixture
def expired_token():
    """创建已过期的JWT令牌"""
    payload = {
        "sub": "test_user",
        "exp": datetime.utcnow() - timedelta(minutes=30),
        "iat": datetime.utcnow() - timedelta(hours=1),
        "username": "test_user"
    }
    return create_test_token(payload)


class TestTokenBlacklistIntegration:
    """令牌黑名单集成测试类"""
    
    async def test_add_and_check_token(self, setup_redis, valid_token):
        """测试添加令牌到黑名单并验证其存在"""
        token_blacklist = setup_redis
        
        # 添加令牌到黑名单
        result = await token_blacklist.add_to_blacklist(valid_token)
        assert result is True
        
        # 检查令牌是否在黑名单中
        is_blacklisted = await token_blacklist.is_blacklisted(valid_token)
        assert is_blacklisted is True
    
    async def test_token_not_in_blacklist(self, setup_redis, valid_token):
        """测试未添加到黑名单的令牌验证"""
        token_blacklist = setup_redis
        
        # 检查未添加的令牌
        is_blacklisted = await token_blacklist.is_blacklisted(valid_token)
        assert is_blacklisted is False
    
    async def test_expired_token_handling(self, setup_redis, expired_token):
        """测试过期令牌的处理"""
        token_blacklist = setup_redis
        
        # 尝试添加过期令牌到黑名单
        result = await token_blacklist.add_to_blacklist(expired_token)
        assert result is True  # 应该能成功添加
        
        # 检查令牌是否在黑名单中
        is_blacklisted = await token_blacklist.is_blacklisted(expired_token)
        assert is_blacklisted is True
    
    async def test_invalid_token_handling(self, setup_redis):
        """测试无效令牌的处理"""
        token_blacklist = setup_redis
        invalid_token = "invalid.jwt.token"
        
        # 尝试添加无效令牌到黑名单
        result = await token_blacklist.add_to_blacklist(invalid_token)
        assert result is False  # 不应该能成功添加
        
        # 检查令牌是否在黑名单中
        is_blacklisted = await token_blacklist.is_blacklisted(invalid_token)
        assert is_blacklisted is False
    
    async def test_token_expiration_in_redis(self, setup_redis, valid_token):
        """测试令牌在Redis中的过期时间设置"""
        token_blacklist = setup_redis
        
        # 解码令牌获取过期时间
        payload = jwt.decode(
            valid_token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": True}
        )
        token_exp = payload.get("exp")
        
        # 模拟Redis的setex方法以捕获过期时间
        original_set = token_blacklist.cache_manager.set
        
        captured_ttl = None
        
        async def mock_set(key, value, ttl=None):
            nonlocal captured_ttl
            captured_ttl = ttl
            return await original_set(key, value, ttl)
        
        # 打补丁替换set方法
        with patch.object(token_blacklist.cache_manager, 'set', side_effect=mock_set):
            await token_blacklist.add_to_blacklist(valid_token)
        
        # 验证TTL是否正确设置
        # 我们期望TTL接近token_exp - current_time
        current_time = int(time.time())
        expected_ttl = max(token_exp - current_time, 0)
        
        # 允许1秒的误差范围
        assert captured_ttl is not None
        assert abs(captured_ttl - expected_ttl) <= 1
    
    @pytest.mark.parametrize("token_valid", [True, False])
    async def test_auth_flow_with_blacklist(self, setup_redis, token_valid):
        """测试令牌黑名单在认证流程中的作用"""
        token_blacklist = setup_redis
        
        # 创建有效令牌
        payload = {
            "sub": "test_user",
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow(),
            "username": "test_user"
        }
        token = create_test_token(payload)
        
        if not token_valid:
            # 将令牌加入黑名单
            await token_blacklist.add_to_blacklist(token)
        
        # 模拟认证系统验证令牌
        # 1. 首先验证令牌是否有效
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            token_valid_signature = True
        except jwt.PyJWTError:
            token_valid_signature = False
        
        assert token_valid_signature is True
        
        # 2. 然后检查令牌是否在黑名单中
        is_blacklisted = await token_blacklist.is_blacklisted(token)
        
        # 验证结果是否符合预期
        assert is_blacklisted is not token_valid 