#!/usr/bin/env python
"""
独立的令牌黑名单测试脚本

这个脚本提供了一个完全独立的实现，用于测试令牌黑名单功能。
它不依赖于项目的其他部分，可以直接运行以验证令牌黑名单的核心逻辑。

主要功能：
1. 模拟Redis客户端实现，提供必要的缓存操作
2. 实现令牌黑名单的核心功能
3. 测试令牌添加和验证的关键路径
4. 处理有效令牌、过期令牌和无效令牌的情况

使用方法：
python standalone_token_blacklist_test.py
"""
import sys
import os
import json
import asyncio
import time
from datetime import datetime, timedelta
import jwt


# 模拟Redis客户端
class MockRedisClient:
    """模拟Redis客户端的简单实现"""
    
    def __init__(self):
        self.cache = {}
        self.timeouts = {}
    
    async def set(self, key, value, ex=None):
        """设置键值对，可选过期时间（秒）"""
        self.cache[key] = value
        if ex is not None:
            # 确保最小TTL为1秒，防止立即过期
            if ex <= 0:
                ex = 3600  # 使用默认1小时
            self.timeouts[key] = time.time() + ex
        return True
    
    async def get(self, key):
        """获取键对应的值"""
        if key in self.cache:
            # 检查是否过期
            if key in self.timeouts and time.time() > self.timeouts[key]:
                del self.cache[key]
                del self.timeouts[key]
                return None
            return self.cache[key]
        return None
    
    async def exists(self, key):
        """检查键是否存在"""
        if key in self.cache:
            # 检查是否过期
            if key in self.timeouts and time.time() > self.timeouts[key]:
                del self.cache[key]
                del self.timeouts[key]
                return 0
            return 1  # 返回1而不是True，模拟真实Redis的行为
        return 0  # 返回0而不是False，模拟真实Redis的行为
    
    async def delete(self, *keys):
        """删除指定的键"""
        count = 0
        for key in keys:
            if key in self.cache:
                del self.cache[key]
                if key in self.timeouts:
                    del self.timeouts[key]
                count += 1
        return count
    
    async def keys(self, pattern="*"):
        """获取符合模式的所有键"""
        # 简单实现，只支持前缀匹配
        prefix = pattern.replace("*", "")
        return [key for key in self.cache.keys() if key.startswith(prefix)]
    
    async def close(self):
        """关闭连接"""
        pass


# 缓存管理器类
class CacheManager:
    """简单的缓存管理器，封装Redis操作"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def set(self, key, value, ttl=None):
        """设置缓存值"""
        return await self.redis.set(key, value, ex=ttl)
    
    async def get(self, key):
        """获取缓存值"""
        return await self.redis.get(key)
    
    async def exists(self, key):
        """检查键是否存在"""
        result = await self.redis.exists(key)
        return bool(result)  # 将Redis返回的整数转换为布尔值
    
    async def delete(self, *keys):
        """删除缓存键"""
        if not keys:
            return 0
        return await self.redis.delete(*keys)
    
    async def keys(self, pattern="*"):
        """获取符合模式的所有键"""
        return await self.redis.keys(pattern)


# 令牌黑名单类
class TokenBlacklist:
    """管理被撤销的JWT令牌"""
    
    def __init__(self, redis_client, key_prefix="jwt_blacklist"):
        """初始化令牌黑名单
        
        Args:
            redis_client: Redis客户端实例
            key_prefix: Redis键的前缀
        """
        self.cache_manager = CacheManager(redis_client)
        self.key_prefix = key_prefix
    
    def _get_key(self, token_id):
        """生成Redis键"""
        return f"{self.key_prefix}:{token_id}"
    
    async def add_to_blacklist(self, token):
        """将令牌添加到黑名单
        
        Args:
            token: JWT令牌字符串
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 解码令牌以获取过期时间和token ID
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            
            # 计算令牌剩余生存时间
            exp_time = payload.get("exp")
            if not exp_time:
                # 如果没有过期时间，使用默认的1小时
                ttl = 3600
            else:
                # 计算剩余时间（秒）
                current_time = int(time.time())
                ttl = max(exp_time - current_time, 0)
                
                # 如果令牌已过期或即将过期，设置一个最小的TTL
                if ttl <= 0:
                    ttl = 3600
            
            # 使用令牌的完整字符串作为标识
            token_id = token
            blacklist_key = self._get_key(token_id)
            
            # 添加到Redis，设置过期时间
            await self.cache_manager.set(blacklist_key, "1", ttl=ttl)
            
            return True
            
        except Exception as e:
            print(f"添加令牌到黑名单失败: {str(e)}")
            return False
    
    async def is_blacklisted(self, token):
        """检查令牌是否在黑名单中
        
        Args:
            token: JWT令牌字符串
            
        Returns:
            bool: 令牌是否在黑名单中
        """
        try:
            # 使用令牌的完整字符串作为标识
            token_id = token
            blacklist_key = self._get_key(token_id)
            
            # 检查Redis中是否存在此键
            exists = await self.cache_manager.exists(blacklist_key)
            
            return exists
            
        except Exception as e:
            print(f"检查令牌黑名单状态失败: {str(e)}")
            return False
    
    async def clear_expired(self):
        """清理所有过期的黑名单记录
        
        Returns:
            int: 清理的记录数量
        """
        # Redis会自动清理过期的键，此方法主要用于测试
        return 0


# JWT配置
JWT_SECRET_KEY = "测试密钥，仅用于测试环境"
JWT_ALGORITHM = "HS256"


# 工具函数
def create_test_token(payload, secret_key=None, algorithm=None):
    """创建测试用的JWT令牌"""
    secret = secret_key or JWT_SECRET_KEY
    alg = algorithm or JWT_ALGORITHM
    return jwt.encode(payload, secret, algorithm=alg)


async def setup_test_environment():
    """设置测试环境"""
    redis_client = MockRedisClient()
    token_blacklist = TokenBlacklist(redis_client)
    return token_blacklist


def generate_test_tokens():
    """生成测试用的令牌"""
    # 有效令牌
    valid_payload = {
        "sub": "test_user",
        "exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "username": "test_user"
    }
    valid_token = create_test_token(valid_payload)
    
    # 过期令牌
    expired_payload = {
        "sub": "test_user",
        "exp": int((datetime.utcnow() - timedelta(minutes=30)).timestamp()),
        "iat": int((datetime.utcnow() - timedelta(hours=1)).timestamp()),
        "username": "test_user"
    }
    expired_token = create_test_token(expired_payload)
    
    # 无效令牌
    invalid_token = "invalid.jwt.token"
    
    return valid_token, expired_token, invalid_token


async def test_token_blacklist():
    """测试令牌黑名单功能"""
    token_blacklist = await setup_test_environment()
    valid_token, expired_token, invalid_token = generate_test_tokens()
    
    # 测试用例结果
    test_results = {}
    
    try:
        # 测试1: 向黑名单添加有效令牌
        print("测试1: 向黑名单添加有效令牌")
        result = await token_blacklist.add_to_blacklist(valid_token)
        assert result is True, "添加有效令牌到黑名单应该返回True"
        test_results["test_add_valid_token"] = "通过"
        print("✅ 测试通过: 成功添加有效令牌到黑名单")
    except AssertionError as e:
        test_results["test_add_valid_token"] = f"失败: {str(e)}"
        print(f"❌ 测试失败: {str(e)}")
    except Exception as e:
        test_results["test_add_valid_token"] = f"错误: {str(e)}"
        print(f"❌ 测试错误: {str(e)}")
    
    try:
        # 测试2: 检查令牌是否在黑名单中
        print("\n测试2: 检查令牌是否在黑名单中")
        is_blacklisted = await token_blacklist.is_blacklisted(valid_token)
        assert is_blacklisted is True, "有效令牌应该在黑名单中"
        test_results["test_is_blacklisted"] = "通过"
        print("✅ 测试通过: 成功确认令牌在黑名单中")
    except AssertionError as e:
        test_results["test_is_blacklisted"] = f"失败: {str(e)}"
        print(f"❌ 测试失败: {str(e)}")
    except Exception as e:
        test_results["test_is_blacklisted"] = f"错误: {str(e)}"
        print(f"❌ 测试错误: {str(e)}")
    
    try:
        # 测试3: 检查未添加的令牌
        print("\n测试3: 检查未添加的令牌")
        is_blacklisted = await token_blacklist.is_blacklisted(expired_token)
        assert is_blacklisted is False, "未添加的令牌不应该在黑名单中"
        test_results["test_is_not_blacklisted"] = "通过"
        print("✅ 测试通过: 成功确认未添加的令牌不在黑名单中")
    except AssertionError as e:
        test_results["test_is_not_blacklisted"] = f"失败: {str(e)}"
        print(f"❌ 测试失败: {str(e)}")
    except Exception as e:
        test_results["test_is_not_blacklisted"] = f"错误: {str(e)}"
        print(f"❌ 测试错误: {str(e)}")
    
    try:
        # 测试4: 添加无效令牌到黑名单
        print("\n测试4: 添加无效令牌到黑名单")
        result = await token_blacklist.add_to_blacklist(invalid_token)
        assert result is False, "添加无效令牌到黑名单应该返回False"
        test_results["test_add_to_blacklist_invalid_token"] = "通过"
        print("✅ 测试通过: 正确处理了无效令牌")
    except AssertionError as e:
        test_results["test_add_to_blacklist_invalid_token"] = f"失败: {str(e)}"
        print(f"❌ 测试失败: {str(e)}")
    except Exception as e:
        test_results["test_add_to_blacklist_invalid_token"] = f"错误: {str(e)}"
        print(f"❌ 测试错误: {str(e)}")
    
    try:
        # 测试5: 检查无效令牌是否在黑名单中
        print("\n测试5: 检查无效令牌是否在黑名单中")
        is_blacklisted = await token_blacklist.is_blacklisted(invalid_token)
        assert is_blacklisted is False, "无效令牌不应该在黑名单中"
        test_results["test_is_blacklisted_invalid_token"] = "通过"
        print("✅ 测试通过: 成功确认无效令牌不在黑名单中")
    except AssertionError as e:
        test_results["test_is_blacklisted_invalid_token"] = f"失败: {str(e)}"
        print(f"❌ 测试失败: {str(e)}")
    except Exception as e:
        test_results["test_is_blacklisted_invalid_token"] = f"错误: {str(e)}"
        print(f"❌ 测试错误: {str(e)}")
    
    return test_results


def run_all_tests():
    """运行所有测试并显示结果"""
    print("===== 开始令牌黑名单测试 =====")
    
    try:
        # 运行令牌黑名单测试
        test_results = asyncio.run(test_token_blacklist())
        
        # 显示测试结果摘要
        print("\n===== 测试结果摘要 =====")
        success_count = 0
        fail_count = 0
        
        for test_name, result in test_results.items():
            if result == "通过":
                success_count += 1
                print(f"✅ {test_name}: {result}")
            else:
                fail_count += 1
                print(f"❌ {test_name}: {result}")
        
        print(f"\n总计: {len(test_results)} 测试, {success_count} 通过, {fail_count} 失败")
        
        # 返回测试是否全部通过
        return fail_count == 0
        
    except Exception as e:
        print(f"测试执行过程中发生错误: {str(e)}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 