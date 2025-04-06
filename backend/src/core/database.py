from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from redis.asyncio import Redis
import os
from urllib.parse import quote_plus
from core.config import settings
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager

# 创建基类
Base = declarative_base()

# 从环境变量获取数据库配置
DB_USER = os.getenv('MYSQL_USER', 'root')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
DB_HOST = os.getenv('MYSQL_HOST', 'localhost')
DB_PORT = int(os.getenv('MYSQL_PORT', '3306'))
DB_NAME = os.getenv('MYSQL_DATABASE', 'autotest')

# 构建数据库URL
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
ASYNC_SQLALCHEMY_DATABASE_URI = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy同步引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# SQLAlchemy异步引擎
async_engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URI,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# 同步会话工厂
SessionLocal = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False
)

# 异步会话工厂
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Redis连接
redis = Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    password=os.getenv('REDIS_PASSWORD', ''),
    decode_responses=True,
    encoding='utf-8'
)

def get_db() -> Generator:
    """获取数据库会话的依赖函数（同步）"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖函数（异步）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_redis() -> Redis:
    """获取Redis连接的依赖函数"""
    return redis 

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        """初始化数据库连接参数"""
        self.config = {
            'host': DB_HOST,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'port': DB_PORT,
            'database': DB_NAME,
            'charset': 'utf8mb4',
            'cursorclass': DictCursor,  # 使用字典游标，结果自动转为dict格式
            'autocommit': True
        }
    
    @contextmanager
    def get_connection(self) -> Generator[pymysql.Connection, None, None]:
        """获取数据库连接（上下文管理器）"""
        conn = None
        try:
            conn = pymysql.connect(**self.config)
            yield conn
        except pymysql.Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self) -> Generator[pymysql.cursors.DictCursor, None, None]:
        """获取数据库游标（上下文管理器）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except pymysql.Error as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def execute(self, sql: str, params: tuple = None) -> int:
        """执行SQL语句
        
        Args:
            sql: SQL语句
            params: SQL参数
            
        Returns:
            影响的行数
        """
        with self.get_cursor() as cursor:
            affected_rows = cursor.execute(sql, params)
            return affected_rows
    
    def execute_many(self, sql: str, params_list: list) -> int:
        """批量执行SQL语句
        
        Args:
            sql: SQL语句
            params_list: SQL参数列表
            
        Returns:
            影响的行数
        """
        with self.get_cursor() as cursor:
            affected_rows = cursor.executemany(sql, params_list)
            return affected_rows
    
    def fetch_one(self, sql: str, params: tuple = None) -> dict:
        """查询单条记录
        
        Args:
            sql: SQL语句
            params: SQL参数
            
        Returns:
            记录字典
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
    
    def fetch_all(self, sql: str, params: tuple = None) -> list:
        """查询多条记录
        
        Args:
            sql: SQL语句
            params: SQL参数
            
        Returns:
            记录字典列表
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def fetch_value(self, sql: str, params: tuple = None):
        """查询单个值
        
        Args:
            sql: SQL语句
            params: SQL参数
            
        Returns:
            单个值
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return row[0] if row else None

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