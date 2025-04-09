"""
数据库连接管理模块
"""
import logging
from contextlib import contextmanager
from typing import Generator, Any, List

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

from core.config import settings
from core.models import Base, create_tables

# 配置日志记录器
logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    poolclass=QueuePool,
    pool_pre_ping=True
)

# 创建会话工厂
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# 创建全局会话实例
session: Session = SessionLocal()

class DatabaseManager:
    """数据库管理器，提供执行SQL语句的方法"""

    @staticmethod
    def execute_sql(sql: str, params: dict = None) -> Any:
        """
        执行SQL语句
        :param sql: SQL语句
        :param params: SQL参数
        :return: 执行结果
        """
        try:
            if params is None:
                params = {}
            result = session.execute(text(sql), params)
            session.commit()
            return result
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"执行SQL出错: {str(e)}")
            raise

    @staticmethod
    def fetch_all(sql: str, params: dict = None) -> list:
        """
        执行查询SQL并返回所有结果
        :param sql: SQL语句
        :param params: SQL参数
        :return: 查询结果列表
        """
        try:
            if params is None:
                params = {}
            result = session.execute(text(sql), params)
            return [dict(row) for row in result]
        except SQLAlchemyError as e:
            logger.error(f"查询数据出错: {str(e)}")
            raise

    @staticmethod
    def fetch_one(sql: str, params: dict = None) -> dict:
        """
        执行查询SQL并返回第一条结果
        :param sql: SQL语句
        :param params: SQL参数
        :return: 查询结果字典
        """
        try:
            if params is None:
                params = {}
            result = session.execute(text(sql), params)
            row = result.first()
            return dict(row) if row else None
        except SQLAlchemyError as e:
            logger.error(f"查询数据出错: {str(e)}")
            raise

def check_tables_exist() -> List[str]:
    """检查所有必需的表是否存在"""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    required_tables = set(Base.metadata.tables.keys())
    missing_tables = required_tables - existing_tables
    return list(missing_tables)

def init_database():
    """初始化数据库"""
    try:
        # 检查数据库连接
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("数据库连接测试成功")
        
        # 创建所有表
        create_tables(engine)
        logger.info("数据库表创建/更新成功")
        
        # 检查是否所有表都创建成功
        missing_tables = check_tables_exist()
        if missing_tables:
            raise RuntimeError(f"表创建失败，缺失的表: {', '.join(missing_tables)}")
        
        logger.info("数据库初始化完成")
        
    except SQLAlchemyError as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"数据库初始化时发生未知错误: {str(e)}")
        raise

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def cleanup():
    """清理数据库连接"""
    try:
        session.close()
        engine.dispose()
        logger.info("数据库连接已清理")
    except Exception as e:
        logger.error(f"清理数据库连接时发生错误: {str(e)}")

# 初始化数据库
try:
    logger.info("开始初始化数据库")
    init_database()
except Exception as e:
    logger.error(f"数据库初始化失败: {str(e)}")
    raise

# 注册退出时的清理函数
import atexit
atexit.register(cleanup)

# 示例用法
if __name__ == "__main__":
    # 查询示例
    sql = "SELECT * FROM users WHERE username = :username"
    params = {"username": "admin"}
    result = DatabaseManager.fetch_one(sql, params)
    print(result)

    # 插入示例
    sql = """
    INSERT INTO users (username, email, password_hash)
    VALUES (:username, :email, :password_hash)
    """
    params = {
        "username": "test_user",
        "email": "test@example.com",
        "password_hash": "hashed_password"
    }
    DatabaseManager.execute_sql(sql, params) 