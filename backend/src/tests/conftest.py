"""
测试配置文件
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

# 导入必要的模块
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from core.config import settings
from core.database import Base, get_session
from main import app
from models.user import User
from tests.utils.auth import create_test_user

# 测试数据库URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    settings.DATABASE_NAME,
    f"{settings.DATABASE_NAME}_test"
)

# 创建测试数据库引擎
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
    
@pytest.fixture(scope="session")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """创建数据库会话"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with TestingSessionLocal() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
        
@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    """创建测试用户"""
    return await create_test_user(db)

# 覆盖依赖项
async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """覆盖数据库会话依赖项"""
    async with TestingSessionLocal() as session:
        yield session
        
app.dependency_overrides[get_session] = override_get_session 

@pytest.fixture(scope="session")
def setup_test_environment():
    """设置测试环境"""
    # 设置测试环境变量
    os.environ["ENV"] = "test"
    os.environ["TESTING"] = "True"
    os.environ["JWT_SECRET_KEY"] = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    
    # 返回测试配置
    return {
        "test_mode": True
    } 