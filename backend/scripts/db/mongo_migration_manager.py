"""MongoDB数据库迁移管理器

提供MongoDB数据库迁移相关功能，包括：
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
from typing import Dict, List, Optional

from .mongo_manager import MongoDBManager

logger = logging.getLogger(__name__)

class MongoDBMigrationManager:
    """MongoDB数据库迁移管理器类"""
    
    VERSION_COLLECTION = 'db_version'
    
    def __init__(
        self,
        mongo_manager: MongoDBManager,
        migrations_dir: str
    ) -> None:
        """初始化迁移管理器
        
        Args:
            mongo_manager: MongoDB管理器实例
            migrations_dir: 迁移文件目录
        """
        self.mongo_manager = mongo_manager
        self.migrations_dir = migrations_dir
        self._ensure_migrations_dir()
        self._ensure_version_collection()
        
    def _ensure_migrations_dir(self) -> None:
        """确保迁移文件目录存在"""
        if not os.path.exists(self.migrations_dir):
            os.makedirs(self.migrations_dir)
            
    def _ensure_version_collection(self) -> None:
        """确保版本集合存在"""
        if self.VERSION_COLLECTION not in self.mongo_manager.get_collection_names():
            # 创建版本集合
            self.mongo_manager.execute_command(
                self.VERSION_COLLECTION,
                "insert",
                {"_id": "schema_version", "current_version": None}
            )
            
            # 创建版本号索引
            self.mongo_manager.create_index(
                self.VERSION_COLLECTION,
                [("version", 1)],
                unique=True
            )
            
    def get_current_version(self) -> Optional[str]:
        """获取当前数据库版本
        
        Returns:
            Optional[str]: 当前版本号，如果没有则返回None
        """
        result = self.mongo_manager.execute_command(
            self.VERSION_COLLECTION,
            "find",
            {"_id": "schema_version"}
        )
        return result[0].get("current_version") if result else None
        
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
            'up': {
                'collections': [],  # 要创建的集合
                'indexes': [],      # 要创建的索引
                'data': []         # 要插入的数据
            },
            'down': {
                'collections': [],  # 要删除的集合
                'indexes': [],      # 要删除的索引
                'data': []         # 要删除的数据
            }
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
        result = self.mongo_manager.execute_command(
            self.VERSION_COLLECTION,
            "find",
            {"version": {"$exists": True}}
        )
        applied_versions = {doc['version'] for doc in result}
        
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
            dry_run: 是否仅打印将要执行的操作而不实际执行
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
                logger.info("将执行以下操作:")
                logger.info(f"- 创建集合: {migration['up']['collections']}")
                logger.info(f"- 创建索引: {migration['up']['indexes']}")
                logger.info(f"- 插入数据: {len(migration['up']['data'])} 条记录")
                continue
                
            try:
                # 创建集合
                for collection in migration['up']['collections']:
                    if collection not in self.mongo_manager.get_collection_names():
                        self.mongo_manager.execute_command(collection, "insert", {})
                        logger.info(f"已创建集合: {collection}")
                        
                # 创建索引
                for index in migration['up']['indexes']:
                    collection_name = index['collection']
                    keys = [(k, v) for k, v in index['keys'].items()]
                    unique = index.get('unique', False)
                    self.mongo_manager.create_index(collection_name, keys, unique)
                    logger.info(f"已创建索引: {collection_name} - {keys}")
                    
                # 插入数据
                for data_item in migration['up']['data']:
                    collection_name = data_item['collection']
                    documents = data_item['documents']
                    self.mongo_manager.execute_command(collection_name, "insert", documents)
                    logger.info(f"已插入数据: {collection_name} - {len(documents)} 条记录")
                    
                # 记录版本
                self.mongo_manager.execute_command(
                    self.VERSION_COLLECTION,
                    "insert",
                    {
                        "version": migration['version'],
                        "description": migration['description'],
                        "applied_at": datetime.now(),
                        "is_applied": True
                    }
                )
                
                # 更新当前版本
                self.mongo_manager.execute_command(
                    self.VERSION_COLLECTION,
                    "update",
                    {
                        "filter": {"_id": "schema_version"},
                        "update": {"$set": {"current_version": migration['version']}}
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
            dry_run: 是否仅打印将要执行的操作而不实际执行
        """
        if steps < 1:
            raise ValueError("回滚步数必须大于0")
            
        # 获取最近的几次迁移
        result = self.mongo_manager.execute_command(
            self.VERSION_COLLECTION,
            "find",
            {"version": {"$exists": True}, "is_applied": True}
        )
        migrations_to_rollback = sorted(
            result,
            key=lambda x: x['version'],
            reverse=True
        )[:steps]
        
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
                logger.info("将执行以下操作:")
                logger.info(f"- 删除集合: {migration['down']['collections']}")
                logger.info(f"- 删除索引: {migration['down']['indexes']}")
                logger.info(f"- 删除数据: {len(migration['down']['data'])} 条记录")
                continue
                
            try:
                # 删除数据
                for data_item in migration['down']['data']:
                    collection_name = data_item['collection']
                    query = data_item['query']
                    self.mongo_manager.execute_command(collection_name, "delete", query)
                    logger.info(f"已删除数据: {collection_name}")
                    
                # 删除索引
                for index in migration['down']['indexes']:
                    collection_name = index['collection']
                    index_name = index['name']
                    self.mongo_manager.drop_index(collection_name, index_name)
                    logger.info(f"已删除索引: {collection_name} - {index_name}")
                    
                # 删除集合
                for collection in migration['down']['collections']:
                    if collection in self.mongo_manager.get_collection_names():
                        self.mongo_manager.execute_command(collection, "drop", None)
                        logger.info(f"已删除集合: {collection}")
                        
                # 更新版本记录
                self.mongo_manager.execute_command(
                    self.VERSION_COLLECTION,
                    "update",
                    {
                        "filter": {"version": version},
                        "update": {"$set": {"is_applied": False}}
                    }
                )
                
                # 更新当前版本
                previous_version = None
                if len(migrations_to_rollback) > 1:
                    previous_version = migrations_to_rollback[1]['version']
                    
                self.mongo_manager.execute_command(
                    self.VERSION_COLLECTION,
                    "update",
                    {
                        "filter": {"_id": "schema_version"},
                        "update": {"$set": {"current_version": previous_version}}
                    }
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
        return self.mongo_manager.execute_command(
            self.VERSION_COLLECTION,
            "find",
            {"version": {"$exists": True}}
        ) 