"""缓存管理器测试模块"""

import pytest
import json
import asyncio
from datetime import timedelta
from unittest.mock import Mock, AsyncMock
from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from core.cache import CacheManager

async def async_return(value):
    """异步返回值的辅助函数"""
    return value

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def redis_mock(redis_client):
    """创建Redis Mock对象"""
    mock = AsyncMock(spec=Redis)
    
    # 设置所有方法返回Future对象
    mock.get.side_effect = lambda key: async_return(None)
    mock.set.side_effect = lambda key, value, **kwargs: async_return(True)
    mock.delete.side_effect = lambda *keys: async_return(1)
    mock.exists.side_effect = lambda key: async_return(1)
    mock.expire.side_effect = lambda key, seconds: async_return(True)
    mock.ttl.side_effect = lambda key: async_return(300)
    mock.incrby.side_effect = lambda key, amount: async_return(1)
    mock.decrby.side_effect = lambda key, amount: async_return(0)
    mock.mget.side_effect = lambda keys: async_return([])
    mock.mset.side_effect = lambda mapping: async_return(True)
    
    # 设置pipeline
    pipeline_mock = AsyncMock()
    pipeline_mock.mset.side_effect = lambda mapping: async_return(True)
    pipeline_mock.expire.side_effect = lambda key, seconds: async_return(True)
    pipeline_mock.execute.side_effect = lambda: async_return([True, True, True])
    mock.pipeline.return_value.__aenter__.return_value = pipeline_mock
    mock.pipeline.return_value.__aexit__.return_value = None
    
    # 设置scan_iter
    async def mock_scan_iter(*args, **kwargs):
        yield "test:prefix:key1"
        yield "test:prefix:key2"
    mock.scan_iter.return_value = mock_scan_iter()
    
    return mock

@pytest.fixture
def cache_manager(redis_mock):
    """创建缓存管理器实例"""
    return CacheManager(
        redis=redis_mock,
        key_prefix="test:",
        default_expire=3600
    )

@pytest.mark.asyncio
async def test_get_cache(cache_manager, redis_mock):
    """测试获取缓存"""
    # 设置mock返回值
    redis_mock.get.side_effect = lambda key: async_return(json.dumps({"key": "value"}))
    
    # 获取缓存
    value = await cache_manager.get("test_key")
    
    # 验证结果
    assert value == {"key": "value"}
    redis_mock.get.assert_called_once_with("test:test_key")

@pytest.mark.asyncio
async def test_get_cache_not_found(cache_manager, redis_mock):
    """测试获取不存在的缓存"""
    # 设置mock返回值
    redis_mock.get.side_effect = lambda key: async_return(None)
    
    # 获取缓存
    value = await cache_manager.get("test_key", default="default")
    
    # 验证结果
    assert value == "default"
    redis_mock.get.assert_called_once_with("test:test_key")

@pytest.mark.asyncio
async def test_set_cache(cache_manager, redis_mock):
    """测试设置缓存"""
    # 设置mock返回值
    redis_mock.set.side_effect = lambda key, value, **kwargs: async_return(True)
    
    # 设置缓存
    result = await cache_manager.set("test_key", {"key": "value"}, expire=60)
    
    # 验证结果
    assert result is True
    redis_mock.set.assert_called_once_with(
        "test:test_key",
        json.dumps({"key": "value"}),
        ex=60,
        nx=False,
        xx=False
    )

@pytest.mark.asyncio
async def test_delete_cache(cache_manager, redis_mock):
    """测试删除缓存"""
    # 设置mock返回值
    redis_mock.delete.side_effect = lambda key: async_return(1)
    
    # 删除缓存
    result = await cache_manager.delete("test_key")
    
    # 验证结果
    assert result is True
    redis_mock.delete.assert_called_once_with("test:test_key")

@pytest.mark.asyncio
async def test_exists_cache(cache_manager, redis_mock):
    """测试检查缓存是否存在"""
    # 设置mock返回值
    redis_mock.exists.side_effect = lambda key: async_return(1)
    
    # 检查缓存
    result = await cache_manager.exists("test_key")
    
    # 验证结果
    assert result is True
    redis_mock.exists.assert_called_once_with("test:test_key")

@pytest.mark.asyncio
async def test_expire_cache(cache_manager, redis_mock):
    """测试设置缓存过期时间"""
    # 设置mock返回值
    redis_mock.expire.side_effect = lambda key, seconds: async_return(True)
    
    # 设置过期时间
    result = await cache_manager.expire("test_key", timedelta(minutes=5))
    
    # 验证结果
    assert result is True
    redis_mock.expire.assert_called_once_with("test:test_key", 300)

@pytest.mark.asyncio
async def test_ttl_cache(cache_manager, redis_mock):
    """测试获取缓存过期时间"""
    # 设置mock返回值
    redis_mock.ttl.side_effect = lambda key: async_return(300)
    
    # 获取过期时间
    result = await cache_manager.ttl("test_key")
    
    # 验证结果
    assert result == 300
    redis_mock.ttl.assert_called_once_with("test:test_key")

@pytest.mark.asyncio
async def test_incr_cache(cache_manager, redis_mock):
    """测试增加计数器值"""
    # 设置mock返回值
    redis_mock.incrby.side_effect = lambda key, amount: async_return(1)
    
    # 增加计数
    result = await cache_manager.incr("test_key")
    
    # 验证结果
    assert result == 1
    redis_mock.incrby.assert_called_once_with("test:test_key", 1)

@pytest.mark.asyncio
async def test_decr_cache(cache_manager, redis_mock):
    """测试减少计数器值"""
    # 设置mock返回值
    redis_mock.decrby.side_effect = lambda key, amount: async_return(0)
    
    # 减少计数
    result = await cache_manager.decr("test_key")
    
    # 验证结果
    assert result == 0
    redis_mock.decrby.assert_called_once_with("test:test_key", 1)

@pytest.mark.asyncio
async def test_mget_cache(cache_manager, redis_mock):
    """测试批量获取缓存"""
    # 设置mock返回值
    redis_mock.mget.side_effect = lambda keys: async_return([
        json.dumps({"key1": "value1"}),
        None,
        json.dumps({"key3": "value3"})
    ])
    
    # 批量获取缓存
    result = await cache_manager.mget(["key1", "key2", "key3"], default="default")
    
    # 验证结果
    assert result == [{"key1": "value1"}, "default", {"key3": "value3"}]
    redis_mock.mget.assert_called_once_with(["test:key1", "test:key2", "test:key3"])

@pytest.mark.asyncio
async def test_mset_cache(cache_manager, redis_mock):
    """测试批量设置缓存"""
    # 设置mock
    pipeline_mock = AsyncMock()
    
    # 设置mset的返回值
    async def mock_mset(mapping):
        return True
    pipeline_mock.mset.side_effect = mock_mset
    
    # 设置expire的返回值
    async def mock_expire(key, seconds):
        return True
    pipeline_mock.expire.side_effect = mock_expire
    
    # 设置execute的返回值
    async def mock_execute():
        return [True] * 3
    pipeline_mock.execute.side_effect = mock_execute
    
    redis_mock.pipeline.return_value.__aenter__.return_value = pipeline_mock
    redis_mock.pipeline.return_value.__aexit__.return_value = None

    # 批量设置缓存
    result = await cache_manager.mset(
        {
            "key1": {"value": 1},
            "key2": {"value": 2}
        },
        expire=60
    )

    # 验证结果
    assert result is True
    pipeline_mock.mset.assert_called_once()
    assert pipeline_mock.expire.call_count == 2

@pytest.mark.asyncio
async def test_delete_many_cache(cache_manager, redis_mock):
    """测试批量删除缓存"""
    # 设置mock返回值
    redis_mock.delete.side_effect = lambda *keys: async_return(2)
    
    # 批量删除缓存
    result = await cache_manager.delete_many(["key1", "key2"])
    
    # 验证结果
    assert result == 2
    redis_mock.delete.assert_called_once_with("test:key1", "test:key2")

@pytest.mark.asyncio
async def test_clear_prefix_cache(cache_manager, redis_mock):
    """测试清除指定前缀的缓存"""
    # 设置mock
    async def mock_scan_iter(*args, **kwargs):
        yield "test:prefix:key1"
        yield "test:prefix:key2"
    redis_mock.scan_iter.return_value = mock_scan_iter()
    redis_mock.delete.side_effect = lambda *keys: async_return(2)
    
    # 清除前缀缓存
    result = await cache_manager.clear_prefix("prefix:")
    
    # 验证结果
    assert result == 2
    redis_mock.scan_iter.assert_called_once_with("test:prefix:*")
    redis_mock.delete.assert_called_once()

@pytest.mark.asyncio
async def test_acquire_lock(cache_manager, redis_mock):
    """测试获取分布式锁"""
    # 设置mock返回值
    redis_mock.set.side_effect = lambda key, value, **kwargs: async_return(True)
    
    # 获取锁
    result = await cache_manager.acquire_lock(
        "test_lock",
        expire=10,
        timeout=5
    )
    
    # 验证结果
    assert result is True
    redis_mock.set.assert_called_once_with(
        "lock:test:test_lock",
        1,
        ex=10,
        nx=True
    )

@pytest.mark.asyncio
async def test_release_lock(cache_manager, redis_mock):
    """测试释放分布式锁"""
    # 设置mock返回值
    redis_mock.delete.side_effect = lambda key: async_return(1)
    
    # 释放锁
    result = await cache_manager.release_lock("test_lock")
    
    # 验证结果
    assert result is True
    redis_mock.delete.assert_called_once_with("lock:test:test_lock")

@pytest.mark.asyncio
async def test_cache_decorator(cache_manager, redis_mock):
    """测试缓存装饰器"""
    # 设置mock
    redis_mock.get.side_effect = lambda key: async_return(None)
    redis_mock.set.side_effect = lambda key, value, **kwargs: async_return(True)
    
    # 定义测试函数
    @cache_manager.cache_decorator("test:{0}:{1}", expire=60)
    async def test_func(arg1, arg2):
        return f"{arg1}_{arg2}"
    
    # 第一次调用，应该执行函数并缓存结果
    result1 = await test_func("a", "b")
    assert result1 == "a_b"

    # 修改mock返回缓存值
    redis_mock.get.side_effect = lambda key: async_return(json.dumps("a_b"))

    # 第二次调用，应该直接返回缓存值
    result2 = await test_func("a", "b")
    assert result2 == "a_b" 