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
from typing import Dict, List, Optional, Tuple, Union

from .mysql_manager import MySQLManager

logger = logging.getLogger(__name__)

class MySQLMigrationManager:
    """MySQL数据库迁移管理器类"""
    
    VERSION_TABLE = 'db_version'
    _counter = 0  # 用于确保版本号唯一性的计数器
    
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
            version VARCHAR(17) NOT NULL,
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
        # 生成版本号 (使用时间戳+计数器)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # 去掉毫秒数
        MySQLMigrationManager._counter += 1
        version = f"{timestamp}{MySQLMigrationManager._counter:02d}"  # 使用2位计数器
        
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
                
            # 检查版本是否已应用
            if migration['version'] not in applied_versions:
                pending_migrations.append(migration)
                
        # 按版本号排序
        return sorted(pending_migrations, key=lambda x: x['version'])
        
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
        # 获取已应用的版本
        query = f"SELECT version FROM {self.VERSION_TABLE} WHERE is_applied = TRUE"
        results = self.mysql_manager.execute_query(query)
        applied_versions = {row['version'] for row in results}
        
        # 获取所有迁移文件
        migrations = []
        for filename in sorted(os.listdir(self.migrations_dir)):
            if not filename.endswith('.json'):
                continue
                
            filepath = os.path.join(self.migrations_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                migration = json.load(f)
                migrations.append(migration)
                
        # 按版本号排序
        migrations.sort(key=lambda x: x['version'])
        
        # 如果指定了版本，验证版本是否存在
        if version:
            version_exists = False
            for migration in migrations:
                if migration['version'] == version:
                    version_exists = True
                    break
            if not version_exists:
                raise ValueError(f"无效的目标版本: {version}")
        
        # 找出需要执行的迁移
        pending_migrations = []
        for migration in migrations:
            if migration['version'] not in applied_versions:
                if version and migration['version'] > version:
                    break
                pending_migrations.append(migration)
                
        if not pending_migrations:
            logger.info("没有待执行的迁移")
            return
            
        # 执行迁移
        for migration in pending_migrations:
            if dry_run:
                logger.info(f"将要执行迁移 {migration['version']}: {migration['description']}")
                for sql in migration['up']:
                    logger.info(f"SQL: {sql}")
                continue
                
            try:
                # 检查up字段是否为空
                if not migration['up']:
                    logger.warning(f"迁移 {migration['version']} 的up字段为空，跳过执行")
                else:
                    # 执行迁移SQL和更新版本记录在同一个事务中
                    sql_statements = migration['up'] + [f"""
                        INSERT INTO {self.VERSION_TABLE} (version, description, is_applied)
                        VALUES (:version, :description, TRUE)
                        ON DUPLICATE KEY UPDATE is_applied = TRUE, description = :description
                    """]
                    params = [{} for _ in migration['up']] + [{
                        'version': migration['version'],
                        'description': migration['description']
                    }]
                    self.mysql_manager.execute_transaction(sql_statements, params)
                
                logger.info(f"已执行迁移 {migration['version']}: {migration['description']}")
                
            except Exception as e:
                logger.error(f"执行迁移 {migration['version']} 失败: {str(e)}")
                raise
                
    def rollback_migration(
        self,
        steps_or_version: Union[int, str] = 1,
        dry_run: bool = False
    ) -> None:
        """回滚迁移
        
        Args:
            steps_or_version: 回滚的步数或目标版本号
            dry_run: 是否仅打印将要执行的SQL而不实际执行
            
        Raises:
            ValueError: 步数无效或版本号无效
        """
        if isinstance(steps_or_version, int):
            if steps_or_version < 1:
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
                {'steps': steps_or_version}
            )
        else:
            # 按版本号回滚
            target_version = steps_or_version
            query = f"""
            SELECT version, description
            FROM {self.VERSION_TABLE}
            WHERE is_applied = TRUE AND version > :target_version
            ORDER BY version DESC
            """
            migrations_to_rollback = self.mysql_manager.execute_query(
                query,
                {'target_version': target_version}
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
                # 执行回滚SQL和更新版本记录在同一个事务中
                sql_statements = migration['down'] + [f"""
                    UPDATE {self.VERSION_TABLE}
                    SET is_applied = FALSE
                    WHERE version = :version
                """]
                params = [{} for _ in migration['down']] + [{'version': version}]
                self.mysql_manager.execute_transaction(sql_statements, params)
                
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