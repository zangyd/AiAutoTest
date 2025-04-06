"""MySQL数据库迁移管理器

提供MySQL数据库迁移相关功能，包括：
- 迁移文件管理
- 版本控制
- 迁移执行
- 迁移回滚
- 迁移历史查询
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .mysql_manager import MySQLManager

logger = logging.getLogger(__name__)

class MySQLMigrationManager:
    """MySQL数据库迁移管理器类"""
    
    VERSION_TABLE = 'db_version'
    
    def __init__(
        self,
        mysql_manager: MySQLManager,
        migrations_dir: str
    ) -> None:
        """初始化迁移管理器
        
        Args:
            mysql_manager: MySQL管理器实例
            migrations_dir: 迁移文件目录
        """
        self.mysql_manager = mysql_manager
        self.migrations_dir = migrations_dir
        self._ensure_migrations_dir()
        self._ensure_version_table()
        
    def _ensure_migrations_dir(self) -> None:
        """确保迁移文件目录存在"""
        if not os.path.exists(self.migrations_dir):
            os.makedirs(self.migrations_dir)
            
    def _ensure_version_table(self) -> None:
        """确保版本表存在"""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.VERSION_TABLE} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            version VARCHAR(14) NOT NULL,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_applied BOOLEAN DEFAULT TRUE
        )
        """
        self.mysql_manager.execute_query(create_table_sql)
        
    def get_current_version(self) -> Optional[str]:
        """获取当前数据库版本
        
        Returns:
            Optional[str]: 当前版本号，如果没有则返回None
        """
        query = f"""
        SELECT version FROM {self.VERSION_TABLE}
        WHERE is_applied = TRUE
        ORDER BY id DESC LIMIT 1
        """
        results = self.mysql_manager.execute_query(query)
        return results[0]['version'] if results else None
        
    def create_migration(self, description: str) -> str:
        """创建新的迁移文件
        
        Args:
            description: 迁移描述
            
        Returns:
            str: 迁移文件路径
        """
        # 生成版本号 (使用时间戳)
        version = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # 创建迁移文件
        filename = f"{version}_{description.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.migrations_dir, filename)
        
        migration_template = {
            'version': version,
            'description': description,
            'up': [],
            'down': []
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(migration_template, f, indent=2, ensure_ascii=False)
            
        return filepath
        
    def get_pending_migrations(self) -> List[Dict]:
        """获取待执行的迁移
        
        Returns:
            List[Dict]: 待执行的迁移列表
        """
        # 获取已应用的版本
        query = f"SELECT version FROM {self.VERSION_TABLE} WHERE is_applied = TRUE"
        results = self.mysql_manager.execute_query(query)
        applied_versions = {row['version'] for row in results}
        
        # 获取所有迁移文件
        pending_migrations = []
        for filename in sorted(os.listdir(self.migrations_dir)):
            if not filename.endswith('.json'):
                continue
                
            filepath = os.path.join(self.migrations_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                migration = json.load(f)
                
            if migration['version'] not in applied_versions:
                pending_migrations.append(migration)
                
        return pending_migrations
        
    def execute_migration(
        self,
        version: Optional[str] = None,
        dry_run: bool = False
    ) -> None:
        """执行迁移
        
        Args:
            version: 目标版本号，为None时迁移到最新版本
            dry_run: 是否仅打印将要执行的SQL而不实际执行
            
        Raises:
            ValueError: 版本号无效
            FileNotFoundError: 迁移文件不存在
        """
        pending = self.get_pending_migrations()
        if not pending:
            logger.info("没有待执行的迁移")
            return
            
        if version:
            # 找到目标版本的位置
            target_index = -1
            for i, migration in enumerate(pending):
                if migration['version'] == version:
                    target_index = i
                    break
            if target_index == -1:
                raise ValueError(f"无效的目标版本: {version}")
            pending = pending[:target_index + 1]
            
        # 执行迁移
        for migration in pending:
            if dry_run:
                logger.info(f"将要执行迁移 {migration['version']}: {migration['description']}")
                for sql in migration['up']:
                    logger.info(f"SQL: {sql}")
                continue
                
            try:
                # 执行迁移SQL
                self.mysql_manager.execute_transaction(migration['up'])
                
                # 记录版本
                insert_sql = f"""
                INSERT INTO {self.VERSION_TABLE} (version, description)
                VALUES (:version, :description)
                """
                self.mysql_manager.execute_query(
                    insert_sql,
                    {
                        'version': migration['version'],
                        'description': migration['description']
                    }
                )
                
                logger.info(f"已执行迁移 {migration['version']}: {migration['description']}")
                
            except Exception as e:
                logger.error(f"执行迁移 {migration['version']} 失败: {str(e)}")
                raise
                
    def rollback_migration(
        self,
        steps: int = 1,
        dry_run: bool = False
    ) -> None:
        """回滚迁移
        
        Args:
            steps: 回滚的步数
            dry_run: 是否仅打印将要执行的SQL而不实际执行
            
        Raises:
            ValueError: 步数无效
        """
        if steps < 1:
            raise ValueError("回滚步数必须大于0")
            
        # 获取最近的几次迁移
        query = f"""
        SELECT version, description
        FROM {self.VERSION_TABLE}
        WHERE is_applied = TRUE
        ORDER BY id DESC
        LIMIT :steps
        """
        migrations_to_rollback = self.mysql_manager.execute_query(
            query,
            {'steps': steps}
        )
        
        if not migrations_to_rollback:
            logger.info("没有可回滚的迁移")
            return
            
        # 按版本号逆序执行回滚
        for migration_record in migrations_to_rollback:
            version = migration_record['version']
            
            # 查找对应的迁移文件
            migration_file = None
            for filename in os.listdir(self.migrations_dir):
                if filename.startswith(version) and filename.endswith('.json'):
                    migration_file = filename
                    break
                    
            if not migration_file:
                raise FileNotFoundError(f"找不到版本 {version} 的迁移文件")
                
            # 读取迁移文件
            filepath = os.path.join(self.migrations_dir, migration_file)
            with open(filepath, 'r', encoding='utf-8') as f:
                migration = json.load(f)
                
            if dry_run:
                logger.info(f"将要回滚迁移 {version}: {migration['description']}")
                for sql in migration['down']:
                    logger.info(f"SQL: {sql}")
                continue
                
            try:
                # 执行回滚SQL
                self.mysql_manager.execute_transaction(migration['down'])
                
                # 更新版本记录
                update_sql = f"""
                UPDATE {self.VERSION_TABLE}
                SET is_applied = FALSE
                WHERE version = :version
                """
                self.mysql_manager.execute_query(
                    update_sql,
                    {'version': version}
                )
                
                logger.info(f"已回滚迁移 {version}: {migration['description']}")
                
            except Exception as e:
                logger.error(f"回滚迁移 {version} 失败: {str(e)}")
                raise
                
    def get_migration_history(self) -> List[Dict]:
        """获取迁移历史
        
        Returns:
            List[Dict]: 迁移历史记录列表
        """
        query = f"""
        SELECT version, description, applied_at, is_applied
        FROM {self.VERSION_TABLE}
        ORDER BY id DESC
        """
        return self.mysql_manager.execute_query(query) 