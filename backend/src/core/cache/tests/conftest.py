"""缓存测试配置文件"""

import os
import pytest
import asyncio
from redis.asyncio import Redis
from redis.exceptions import ConnectionError
from unittest.mock import AsyncMock
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

@pytest.fixture(scope="session")
async def redis_client():
    """创建Redis客户端并检查连接"""
    try:
        client = Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True
        )
        # 测试连接
        await client.ping()
        yield client
        # 关闭连接
        await client.close()
    except ConnectionError as e:
        pytest.skip(f"Redis连接失败: {str(e)}")
    except Exception as e:
        pytest.fail(f"Redis初始化失败: {str(e)}")

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def redis_mock():
    """创建Redis Mock对象"""
    mock = AsyncMock(spec=Redis)
    mock.ping.return_value = True
    return mock 