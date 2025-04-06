"""MySQL数据库管理器

提供MySQL数据库的连接管理、SQL执行、事务处理、表结构查询、数据库备份和恢复、连接池管理等功能。
"""

import os
import subprocess
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlparse

class MySQLManager:
    """MySQL数据库管理器类"""
    
    def __init__(
        self,
        url: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True
    ):
        """初始化MySQL管理器
        
        Args:
            url: 数据库连接URL
            echo: 是否打印SQL语句
            pool_size: 连接池大小
            max_overflow: 连接池最大溢出连接数
            pool_timeout: 连接池获取连接超时时间
            pool_recycle: 连接池回收时间
            pool_pre_ping: 是否在使用前ping数据库
        """
        self.url = url
        self.engine = create_engine(
            url,
            echo=echo,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping
        )
        
    def check_connection(self) -> bool:
        """检查数据库连接是否正常
        
        Returns:
            bool: 连接正常返回True，否则返回False
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False
            
    def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """执行SQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            Optional[List[Dict[str, Any]]]: 查询结果列表，如果不是SELECT语句则返回None
            
        Raises:
            SQLAlchemyError: 数据库操作错误
        """
        # 判断是否为SELECT语句
        is_select = query.upper().strip().startswith(("SELECT", "SHOW"))
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            if not is_select:
                conn.commit()
                return None
            return [dict(zip(result.keys(), row)) for row in result.fetchall()]
            
    def execute_transaction(
        self,
        statements: List[str],
        params_list: List[Dict[str, Any]]
    ) -> None:
        """执行事务
        
        Args:
            statements: SQL语句列表
            params_list: 参数列表
            
        Raises:
            SQLAlchemyError: 事务执行错误
        """
        if len(statements) != len(params_list):
            raise ValueError("SQL语句数量与参数列表数量不匹配")
            
        with self.engine.begin() as conn:
            for statement, params in zip(statements, params_list):
                conn.execute(text(statement), params)
                
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            Dict[str, Any]: 表结构信息
        """
        inspector = inspect(self.engine)
        
        return {
            "columns": inspector.get_columns(table_name),
            "primary_keys": inspector.get_pk_constraint(table_name),
            "indexes": inspector.get_indexes(table_name),
            "foreign_keys": inspector.get_foreign_keys(table_name)
        }
        
    def backup_database(self, backup_path: str) -> None:
        """备份数据库
        
        Args:
            backup_path: 备份文件路径
        """
        # 从URL中解析数据库连接信息
        parsed = urlparse(self.url)
        db_name = parsed.path.lstrip('/')
        username = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 3306
        
        # 执行mysqldump命令
        cmd = [
            "mysqldump",
            f"-h{host}",
            f"-P{port}",
            f"-u{username}",
            f"-p{password}",
            "--single-transaction",
            "--routines",
            "--triggers",
            "--events",
            db_name
        ]
        
        with open(backup_path, "w") as f:
            subprocess.run(cmd, stdout=f, check=True)
            
    def restore_database(self, backup_path: str) -> None:
        """从备份文件恢复数据库
        
        Args:
            backup_path: 备份文件路径
        """
        # 从URL中解析数据库连接信息
        parsed = urlparse(self.url)
        db_name = parsed.path.lstrip('/')
        username = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 3306
        
        # 执行mysql命令
        cmd = [
            "mysql",
            f"-h{host}",
            f"-P{port}",
            f"-u{username}",
            f"-p{password}",
            db_name
        ]
        
        with open(backup_path, "r") as f:
            subprocess.run(cmd, stdin=f, check=True)
            
    def get_pool_status(self) -> Dict[str, int]:
        """获取连接池状态
        
        Returns:
            Dict[str, int]: 连接池状态信息
        """
        pool = self.engine.pool
        return {
            "total_connections": pool.size() + pool.overflow(),
            "active_connections": pool.checkedin() + pool.checkedout(),
            "idle_connections": pool.checkedin(),
            "overflow_count": pool.overflow(),
            "reconnect_count": 0  # 添加reconnect_count字段
        }
        
    def clear_pool(self) -> None:
        """清理连接池"""
        self.engine.dispose()
        
    def close(self) -> None:
        """关闭数据库连接"""
        self.clear_pool() 