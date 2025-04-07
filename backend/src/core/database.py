"""
数据库连接管理模块
"""
import os
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from redis.asyncio import Redis
from urllib.parse import quote_plus
from core.config import settings
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
import redis

# 创建数据库基类
Base = declarative_base()

def get_database_url(database_name: str = None) -> str:
    """
    获取数据库URL
    """
    db_name = database_name or settings.MYSQL_DATABASE
    return (
        f"mysql+pymysql://{settings.MYSQL_USER}:{quote_plus(settings.MYSQL_PASSWORD)}"
        f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{db_name}"
    )

def get_async_database_url(database_name: str = None) -> str:
    """
    获取异步数据库URL
    """
    db_name = database_name or settings.MYSQL_DATABASE
    return (
        f"mysql+aiomysql://{settings.MYSQL_USER}:{quote_plus(settings.MYSQL_PASSWORD)}"
        f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{db_name}"
    )

# 创建同步数据库引擎
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    echo=settings.SQLALCHEMY_ECHO
)

# 创建异步数据库引擎
async_engine = create_engine(
    get_async_database_url(),
    pool_pre_ping=True,
    echo=settings.SQLALCHEMY_ECHO
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine)

def get_db() -> Generator:
    """
    获取数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> Generator:
    """
    获取异步数据库会话
    """
    async_db = AsyncSessionLocal()
    try:
        yield async_db
    finally:
        await async_db.close()

# 创建Redis客户端
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,
    decode_responses=True
)

def get_redis() -> redis.Redis:
    """
    获取Redis客户端
    """
    return redis_client

class DatabaseManager:
    """
    数据库管理器
    """
    
    def __init__(self, db_session=None):
        """
        初始化数据库管理器
        """
        self.db = db_session or next(get_db())
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def execute(self, sql, params=None):
        """
        执行SQL语句
        """
        try:
            result = self.db.execute(sql, params or {})
            self.db.commit()
            return result
        except Exception as e:
            self.db.rollback()
            raise e
    
    def fetch_all(self, sql, params=None):
        """
        获取所有结果
        """
        result = self.execute(sql, params)
        return result.fetchall()
    
    def fetch_one(self, sql, params=None):
        """
        获取单个结果
        """
        result = self.execute(sql, params)
        return result.fetchone()

# 创建全局数据库管理器实例
db = DatabaseManager()

# 示例用法
if __name__ == '__main__':
    # 查询示例
    sql = "SELECT * FROM users WHERE username = %s"
    user = db.fetch_one(sql, ('admin',))
    if user:
        print(f"用户信息: {user}")
    
    # 插入示例
    sql = "INSERT INTO users (username, email) VALUES (%s, %s)"
    affected = db.execute(sql, ('test_user', 'test@example.com'))
    print(f"插入影响行数: {affected}")
    
    # 批量插入示例
    sql = "INSERT INTO users (username, email) VALUES (%s, %s)"
    users = [
        ('user1', 'user1@example.com'),
        ('user2', 'user2@example.com')
    ]
    affected = db.execute_many(sql, users)
    print(f"批量插入影响行数: {affected}") 