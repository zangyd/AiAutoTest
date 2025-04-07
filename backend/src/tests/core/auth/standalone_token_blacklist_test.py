"""独立的令牌黑名单测试脚本"""
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

# 添加项目根目录到Python路径
backend_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

# 设置测试环境变量
os.environ["ENV"] = "test"
os.environ["TESTING"] = "True"
os.environ["JWT_SECRET_KEY"] = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
os.environ["JWT_ALGORITHM"] = "HS256"

# 导入必要的模块
import jwt
import time
from core.auth.token_blacklist import TokenBlacklist
from core.config.settings import settings

def create_mock_redis():
    """创建模拟Redis客户端"""
    redis_mock = AsyncMock()
    
    # 模拟Redis方法
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = True
    redis_mock.exists.return_value = False
    
    return redis_mock

def create_token_blacklist(mock_redis):
    """创建令牌黑名单实例"""
    return TokenBlacklist(mock_redis)

def create_test_token():
    """创建测试令牌"""
    payload = {
        "sub": "1",
        "username": "testuser",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

async def test_add_to_blacklist():
    """测试将令牌添加到黑名单"""
    # 准备测试数据
    mock_redis = create_mock_redis()
    token_blacklist = create_token_blacklist(mock_redis)
    test_token = create_test_token()
    
    # 将令牌添加到黑名单
    result = await token_blacklist.add_to_blacklist(test_token)
    
    # 断言
    assert result is True, "添加令牌到黑名单应返回True"
    mock_redis.set.assert_called_once()
    print("✅ test_add_to_blacklist 通过")

async def test_is_blacklisted():
    """测试检查令牌是否在黑名单中"""
    # 准备测试数据
    mock_redis = create_mock_redis()
    token_blacklist = create_token_blacklist(mock_redis)
    test_token = create_test_token()
    
    # 设置模拟返回值
    mock_redis.exists.return_value = True
    
    # 检查令牌是否在黑名单中
    result = await token_blacklist.is_blacklisted(test_token)
    
    # 断言
    assert result is True, "检查黑名单中的令牌应返回True"
    mock_redis.exists.assert_called_once()
    print("✅ test_is_blacklisted 通过")

async def test_is_not_blacklisted():
    """测试检查令牌不在黑名单中"""
    # 准备测试数据
    mock_redis = create_mock_redis()
    token_blacklist = create_token_blacklist(mock_redis)
    test_token = create_test_token()
    
    # 设置模拟返回值
    mock_redis.exists.return_value = False
    
    # 检查令牌是否在黑名单中
    result = await token_blacklist.is_blacklisted(test_token)
    
    # 断言
    assert result is False, "检查不在黑名单中的令牌应返回False"
    mock_redis.exists.assert_called_once()
    print("✅ test_is_not_blacklisted 通过")

async def test_add_to_blacklist_invalid_token():
    """测试将无效令牌添加到黑名单"""
    # 准备测试数据
    mock_redis = create_mock_redis()
    token_blacklist = create_token_blacklist(mock_redis)
    
    # 将无效令牌添加到黑名单
    result = await token_blacklist.add_to_blacklist("invalid_token")
    
    # 断言
    assert result is False, "添加无效令牌到黑名单应返回False"
    mock_redis.set.assert_not_called()
    print("✅ test_add_to_blacklist_invalid_token 通过")

async def test_is_blacklisted_invalid_token():
    """测试检查无效令牌是否在黑名单中"""
    # 准备测试数据
    mock_redis = create_mock_redis()
    token_blacklist = create_token_blacklist(mock_redis)
    
    # 设置模拟返回值
    mock_redis.exists.return_value = False
    
    # 检查无效令牌是否在黑名单中
    result = await token_blacklist.is_blacklisted("invalid_token")
    
    # 断言
    assert result is False, "检查无效令牌是否在黑名单中应返回False"
    mock_redis.exists.assert_called_once_with("invalid_token")
    print("✅ test_is_blacklisted_invalid_token 通过")

async def run_all_tests():
    """运行所有测试"""
    print("开始运行令牌黑名单测试...\n")
    
    try:
        await test_add_to_blacklist()
        await test_is_blacklisted()
        await test_is_not_blacklisted()
        await test_add_to_blacklist_invalid_token()
        await test_is_blacklisted_invalid_token()
        
        print("\n所有测试通过！")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 