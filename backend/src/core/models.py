"""
SQLAlchemy基础模型定义
"""
from typing import Any, Dict, List
from sqlalchemy import MetaData, inspect, event, Table
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    registry,
    MappedAsDataclass
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import CreateTable, ForeignKeyConstraint, Table as SchemaTable
from sqlalchemy.sql.ddl import DDL
import logging

# 配置日志记录器
logger = logging.getLogger(__name__)

# 创建命名约定的metadata
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# 创建metadata实例
metadata = MetaData(naming_convention=convention)

# 创建registry实例
mapper_registry = registry()

class Base(DeclarativeBase):
    """SQLAlchemy声明式基类"""
    
    # 使用registry的metadata
    metadata = metadata
    
    # 类型注解
    __abstract__ = True
    
    # 自动生成表名
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """将驼峰命名转换为下划线命名作为表名"""
        import re
        # 将大写字母转换为下划线+小写字母
        name = re.sub('(?!^)([A-Z])', r'_\1', cls.__name__).lower()
        # 处理复数形式
        if not name.endswith('s'):
            name += 's'
        return name
    
    # 自动设置表选项
    @declared_attr.directive
    def __table_args__(cls) -> Dict:
        """设置默认的表选项"""
        return {
            'mysql_engine': 'InnoDB',  # 使用InnoDB引擎
            'mysql_charset': 'utf8mb4',  # 使用utf8mb4字符集
            'mysql_collate': 'utf8mb4_unicode_ci',  # 使用unicode排序规则
            'extend_existing': True  # 允许表重定义
        }

    def to_dict(self) -> Dict:
        """将模型转换为字典"""
        return {
            column.key: getattr(self, column.key)
            for column in inspect(self).mapper.column_attrs
        }

    @classmethod
    def get_table_name(cls) -> str:
        """获取表名"""
        return cls.__tablename__

    @classmethod
    def get_primary_keys(cls) -> List[str]:
        """获取主键字段名列表"""
        return [key.name for key in inspect(cls).primary_key]

    @classmethod
    def get_columns(cls) -> List[str]:
        """获取所有字段名列表"""
        return [column.key for column in inspect(cls).mapper.column_attrs]

    @classmethod
    def get_relationships(cls) -> List[str]:
        """获取所有关系字段名列表"""
        return [rel.key for rel in inspect(cls).mapper.relationships]

def create_tables(engine):
    """创建不存在的表"""
    try:
        # 获取所有表
        tables = Base.metadata.tables
        
        # 获取已存在的表
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        
        # 创建不存在的表
        for table_name, table in tables.items():
            if table_name not in existing_tables:
                logger.info(f"创建表: {table_name}")
                table.create(engine)
        logger.info("所有缺失的表创建完成")
        
    except Exception as e:
        logger.error(f"创建表时发生错误: {str(e)}")
        raise

# 监听表创建事件
@event.listens_for(Base.metadata, 'after_create')
def receive_after_create(target, connection, **kw):
    """在创建表之后，创建关联表"""
    from core.auth.models import role_permissions, user_roles, user_departments
    
    # 创建关联表
    for table in [role_permissions, user_roles, user_departments]:
        if not inspect(connection).has_table(table.name):
            table.create(connection) 