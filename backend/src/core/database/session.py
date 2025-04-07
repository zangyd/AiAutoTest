"""数据库会话模块"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,
    pool_size=settings.POOL_SIZE,
    echo=settings.ECHO_SQL
)

# 创建会话生成器
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型
Base = declarative_base()

# 创建会话
session = SessionLocal()

def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    
    Yields:
        Session: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 