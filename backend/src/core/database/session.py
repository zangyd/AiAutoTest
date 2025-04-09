"""
数据库会话管理模块
"""
from typing import Generator
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from core.config.settings import settings
from core.utils.logger import Logger
from core.models import Base, metadata

# 配置日志记录器
logger = Logger(
    name="database",
    level=settings.LOG_LEVEL,
    console_color=True
)

# 创建数据库引擎
try:
    # 对密码进行URL编码
    encoded_password = quote_plus(settings.MYSQL_PASSWORD)
    
    # 构建数据库URL
    database_url = (
        f"mysql+pymysql://{settings.MYSQL_USER}:{encoded_password}@"
        f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
    )
    
    # 创建引擎
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        echo=settings.DATABASE_ECHO_SQL,
        connect_args={
            "charset": "utf8mb4"
        }
    )
    logger.info("数据库引擎创建成功")
except Exception as e:
    logger.error(f"数据库引擎创建失败: {str(e)}")
    raise

# 创建会话工厂
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# 创建全局会话
session = SessionLocal()

def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    
    Yields:
        Session: 数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"数据库会话异常: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db() -> None:
    """
    初始化数据库
    
    如果配置了自动创建表，则创建所有表
    """
    try:
        if settings.AUTO_CREATE_TABLES:
            Base.metadata.create_all(bind=engine)
            logger.info("数据库表创建成功")
    except SQLAlchemyError as e:
        logger.error(f"数据库表创建失败: {str(e)}")
        raise

# 确保程序退出时关闭会话
import atexit

@atexit.register
def cleanup():
    """程序退出时清理资源"""
    try:
        session.close()
        logger.info("数据库会话已清理")
    except Exception as e:
        logger.error(f"数据库会话清理失败: {str(e)}")

# 导出所需的对象
__all__ = ['get_db', 'session', 'Base', 'metadata', 'engine'] 