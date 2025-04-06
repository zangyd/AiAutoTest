"""MongoDB数据库管理器

提供MongoDB数据库管理相关功能，包括：
- 连接管理
- 集合操作
- 数据备份和恢复
- 索引管理
- 聚合操作
- 复制集支持
- 监控功能
- 性能优化
- 错误处理
"""

import os
import json
import logging
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable
from urllib.parse import urlparse
from functools import wraps
from contextlib import contextmanager

from pymongo import MongoClient, ReadPreference, ASCENDING, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import (
    OperationFailure,
    NetworkTimeout,
    ConnectionFailure,
    ServerSelectionTimeoutError,
    WriteError,
    BulkWriteError
)

logger = logging.getLogger(__name__)

def retry_on_error(retries: int = 3, delay: float = 1.0):
    """重试装饰器
    
    Args:
        retries: 重试次数
        delay: 重试延迟(秒)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except (NetworkTimeout, ConnectionFailure, ServerSelectionTimeoutError) as e:
                    last_error = e
                    if attempt < retries - 1:
                        logger.warning(f"操作失败，{delay}秒后重试: {str(e)}")
                        time.sleep(delay)
                    continue
            raise last_error
        return wrapper
    return decorator

class MongoDBManager:
    """MongoDB数据库管理器类"""
    
    def __init__(
        self,
        mongo_url: str,
        max_pool_size: int = 100,
        min_pool_size: int = 10,
        max_idle_time_ms: int = 10000,
        connect_timeout_ms: int = 5000,
        server_selection_timeout_ms: int = 5000
    ) -> None:
        """初始化MongoDB管理器
        
        Args:
            mongo_url: MongoDB连接URL
            max_pool_size: 最大连接池大小
            min_pool_size: 最小连接池大小
            max_idle_time_ms: 最大空闲时间(毫秒)
            connect_timeout_ms: 连接超时时间(毫秒)
            server_selection_timeout_ms: 服务器选择超时时间(毫秒)
        """
        self.mongo_url = mongo_url
        self.max_pool_size = max_pool_size
        self.min_pool_size = min_pool_size
        self.max_idle_time_ms = max_idle_time_ms
        self.connect_timeout_ms = connect_timeout_ms
        self.server_selection_timeout_ms = server_selection_timeout_ms
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        self._connect()
        
    def _connect(self) -> None:
        """连接到MongoDB数据库"""
        try:
            # 解析URL获取数据库名
            parsed_url = urlparse(self.mongo_url)
            db_name = parsed_url.path.lstrip('/')
            
            # 创建客户端连接
            self._client = MongoClient(
                self.mongo_url,
                maxPoolSize=self.max_pool_size,
                minPoolSize=self.min_pool_size,
                maxIdleTimeMS=self.max_idle_time_ms,
                connectTimeoutMS=self.connect_timeout_ms,
                serverSelectionTimeoutMS=self.server_selection_timeout_ms,
                retryWrites=True,
                w='majority'  # 写入确认
            )
            self._db = self._client[db_name]
            
            logger.info(f"已连接到MongoDB数据库: {db_name}")
        except Exception as e:
            logger.error(f"连接MongoDB失败: {str(e)}")
            raise

    @contextmanager
    def _operation_context(self, operation_name: str):
        """操作上下文管理器
        
        Args:
            operation_name: 操作名称
        """
        start_time = time.time()
        try:
            yield
        except Exception as e:
            logger.error(f"{operation_name}失败: {str(e)}")
            raise
        finally:
            duration = time.time() - start_time
            logger.debug(f"{operation_name}耗时: {duration:.3f}秒")

    @retry_on_error()
    def check_connection(self) -> bool:
        """检查数据库连接状态
        
        Returns:
            bool: 连接是否正常
        """
        with self._operation_context("检查连接"):
            self._client.admin.command('ping')
            return True

    def close(self) -> None:
        """关闭数据库连接"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None

    def get_pool_status(self) -> Dict:
        """获取连接池状态
        
        Returns:
            Dict: 连接池状态信息
        """
        if not self._client:
            return {}
            
        return {
            "max_pool_size": self.max_pool_size,
            "min_pool_size": self.min_pool_size,
            "max_idle_time_ms": self.max_idle_time_ms,
            "active_connections": len(self._client._topology._servers)
        }

    @retry_on_error()
    def execute_command(
        self,
        collection_name: str,
        command: str,
        data: Optional[Union[Dict, List[Dict]]] = None,
        batch_size: int = 1000
    ) -> List[Dict]:
        """执行MongoDB命令
        
        Args:
            collection_name: 集合名称
            command: 命令名称 (insert/find/update/delete)
            data: 命令参数
            batch_size: 批处理大小
            
        Returns:
            List[Dict]: 执行结果
            
        Raises:
            ValueError: 无效的命令
            WriteError: 写入错误
            BulkWriteError: 批量写入错误
        """
        with self._operation_context(f"执行{command}命令"):
            collection = self._db[collection_name]
            
            try:
                if command == "insert":
                    if isinstance(data, list):
                        # 批量插入
                        results = []
                        for i in range(0, len(data), batch_size):
                            batch = data[i:i + batch_size]
                            result = collection.insert_many(batch, ordered=False)
                            results.append({
                                "inserted_ids": [str(id) for id in result.inserted_ids]
                            })
                        return results
                    else:
                        result = collection.insert_one(data)
                        return [{"inserted_id": str(result.inserted_id)}]
                        
                elif command == "find":
                    query = data or {}
                    cursor = collection.find(query).batch_size(batch_size)
                    return list(cursor)
                    
                elif command == "update":
                    if not isinstance(data, dict) or "filter" not in data or "update" not in data:
                        raise ValueError("更新命令需要filter和update参数")
                    result = collection.update_many(
                        data["filter"],
                        data["update"],
                        upsert=data.get("upsert", False)
                    )
                    return [{
                        "matched_count": result.matched_count,
                        "modified_count": result.modified_count,
                        "upserted_id": str(result.upserted_id) if result.upserted_id else None
                    }]
                    
                elif command == "delete":
                    result = collection.delete_many(data or {})
                    return [{"deleted_count": result.deleted_count}]
                    
                else:
                    raise ValueError(f"无效的命令: {command}")
                    
            except WriteError as e:
                logger.error(f"写入错误: {str(e)}")
                raise
            except BulkWriteError as e:
                logger.error(f"批量写入错误: {str(e)}")
                raise

    @retry_on_error()
    def backup_database(
        self,
        backup_path: str,
        collections: Optional[List[str]] = None,
        compress: bool = True
    ) -> None:
        """备份数据库
        
        Args:
            backup_path: 备份文件路径
            collections: 要备份的集合列表
            compress: 是否压缩备份
        """
        with self._operation_context("备份数据库"):
            try:
                # 解析连接URL
                parsed_url = urlparse(self.mongo_url)
                host = parsed_url.hostname
                port = parsed_url.port or 27017
                db_name = parsed_url.path.lstrip('/')
                
                # 构建mongodump命令
                cmd = [
                    "mongodump",
                    "--host", host,
                    "--port", str(port),
                    "--db", db_name,
                    "--out", backup_path
                ]
                
                # 添加压缩选项
                if compress:
                    cmd.append("--gzip")
                
                # 添加认证信息
                if parsed_url.username and parsed_url.password:
                    cmd.extend([
                        "--username", parsed_url.username,
                        "--password", parsed_url.password,
                        "--authenticationDatabase", "admin"
                    ])
                    
                # 添加集合过滤
                if collections:
                    for collection in collections:
                        cmd.extend(["--collection", collection])
                        
                # 执行备份
                subprocess.run(cmd, check=True, capture_output=True)
                logger.info(f"数据库已备份到: {backup_path}")
                
            except subprocess.CalledProcessError as e:
                logger.error(f"备份数据库失败: {e.stderr.decode()}")
                raise

    def get_collection_names(self) -> List[str]:
        """获取所有集合名称
        
        Returns:
            List[str]: 集合名称列表
        """
        return self._db.list_collection_names()
        
    def get_collection_info(self, collection_name: str) -> Dict:
        """获取集合信息
        
        Args:
            collection_name: 集合名称
            
        Returns:
            Dict: 集合信息
        """
        collection = self._db[collection_name]
        
        # 获取集合统计信息
        stats = self._db.command("collstats", collection_name)
        
        # 获取索引信息
        indexes = list(collection.list_indexes())
        
        return {
            "name": collection_name,
            "document_count": stats["count"],
            "size": stats["size"],
            "avg_document_size": stats.get("avgObjSize", 0),
            "indexes": indexes
        }
        
    def restore_database(self, backup_path: str) -> None:
        """从备份恢复数据库
        
        Args:
            backup_path: 备份文件路径
        """
        try:
            # 解析连接URL
            parsed_url = urlparse(self.mongo_url)
            host = parsed_url.hostname
            port = parsed_url.port or 27017
            db_name = parsed_url.path.lstrip('/')
            
            # 构建mongorestore命令
            cmd = [
                "mongorestore",
                "--host", host,
                "--port", str(port),
                "--db", db_name,
                "--drop",  # 恢复前删除现有集合
                os.path.join(backup_path, db_name)
            ]
            
            # 添加认证信息
            if parsed_url.username and parsed_url.password:
                cmd.extend([
                    "--username", parsed_url.username,
                    "--password", parsed_url.password,
                    "--authenticationDatabase", "admin"
                ])
                
            # 执行恢复
            subprocess.run(cmd, check=True)
            logger.info("数据库恢复完成")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"恢复数据库失败: {str(e)}")
            raise
            
    def create_index(
        self,
        collection_name: str,
        keys: List[tuple],
        unique: bool = False
    ) -> str:
        """创建索引
        
        Args:
            collection_name: 集合名称
            keys: 索引键列表，每个元素为(字段名, 排序方向)元组
            unique: 是否唯一索引
            
        Returns:
            str: 创建的索引名称
        """
        collection = self._db[collection_name]
        return collection.create_index(keys, unique=unique)
        
    def drop_index(self, collection_name: str, index_name: str) -> None:
        """删除索引
        
        Args:
            collection_name: 集合名称
            index_name: 索引名称
        """
        collection = self._db[collection_name]
        collection.drop_index(index_name)
        
    def aggregate(
        self,
        collection_name: str,
        pipeline: List[Dict],
        allow_disk_use: bool = False
    ) -> List[Dict]:
        """执行聚合操作
        
        Args:
            collection_name: 集合名称
            pipeline: 聚合管道
            allow_disk_use: 是否允许使用磁盘
            
        Returns:
            List[Dict]: 聚合结果
        """
        collection = self._db[collection_name]
        return list(collection.aggregate(pipeline, allowDiskUse=allow_disk_use))
        
    def map_reduce(
        self,
        collection_name: str,
        map_function: str,
        reduce_function: str,
        output: str,
        query: Optional[Dict] = None
    ) -> List[Dict]:
        """执行MapReduce操作
        
        Args:
            collection_name: 集合名称
            map_function: Map函数(JavaScript)
            reduce_function: Reduce函数(JavaScript)
            output: 输出集合名称
            query: 查询条件
            
        Returns:
            List[Dict]: MapReduce结果
        """
        collection = self._db[collection_name]
        
        # 解析map函数中的emit操作
        # 假设map函数格式为: function() { emit(this.field, value); }
        emit_field = map_function.split('emit(this.')[1].split(',')[0].strip()
        
        # 构建等效的聚合管道
        pipeline = []
        
        # 添加查询条件
        if query:
            pipeline.append({"$match": query})
            
        # 添加分组操作
        pipeline.append({
            "$group": {
                "_id": f"${emit_field}",
                "value": {"$sum": 1}  # 默认计数
            }
        })
        
        # 执行聚合
        result_collection = self._db[output]
        results = list(collection.aggregate(pipeline))
        
        # 将结果保存到输出集合
        if results:
            result_collection.drop()  # 清除现有数据
            result_collection.insert_many(results)
            
        return results
        
    def create_compound_index(
        self,
        collection_name: str,
        keys: List[tuple],
        **kwargs
    ) -> str:
        """创建复合索引
        
        Args:
            collection_name: 集合名称
            keys: 索引键列表，每个元素为(字段名, 排序方向)元组
            **kwargs: 其他索引选项
            
        Returns:
            str: 创建的索引名称
        """
        collection = self._db[collection_name]
        return collection.create_index(keys, **kwargs)
        
    def create_ttl_index(
        self,
        collection_name: str,
        field: str,
        expiration_seconds: int
    ) -> str:
        """创建TTL索引
        
        Args:
            collection_name: 集合名称
            field: 时间字段名
            expiration_seconds: 过期时间(秒)
            
        Returns:
            str: 创建的索引名称
        """
        collection = self._db[collection_name]
        return collection.create_index(
            [(field, 1)],
            expireAfterSeconds=expiration_seconds
        )
        
    def create_geospatial_index(
        self,
        collection_name: str,
        field: str,
        index_type: str = "2dsphere"
    ) -> str:
        """创建地理空间索引
        
        Args:
            collection_name: 集合名称
            field: 地理坐标字段名
            index_type: 索引类型(2d/2dsphere)
            
        Returns:
            str: 创建的索引名称
        """
        collection = self._db[collection_name]
        return collection.create_index([(field, index_type)])
        
    def configure_replica_set(
        self,
        replica_set_name: str,
        members: List[Dict]
    ) -> Dict:
        """配置复制集
        
        Args:
            replica_set_name: 复制集名称
            members: 成员节点配置列表
            
        Returns:
            Dict: 配置结果
        """
        config = {
            "_id": replica_set_name,
            "members": members
        }
        try:
            result = self._client.admin.command("replSetInitiate", config)
            logger.info(f"复制集 {replica_set_name} 配置成功")
            return result
        except Exception as e:
            logger.error(f"配置复制集失败: {str(e)}")
            raise
            
    def get_replica_set_status(self) -> Dict:
        """获取复制集状态
        
        Returns:
            Dict: 复制集状态信息
        """
        try:
            return self._client.admin.command("replSetGetStatus")
        except Exception as e:
            logger.error(f"获取复制集状态失败: {str(e)}")
            raise
            
    def step_down_primary(self, timeout_secs: int = 60) -> Dict:
        """主节点降级
        
        Args:
            timeout_secs: 超时时间(秒)
            
        Returns:
            Dict: 操作结果
        """
        try:
            return self._client.admin.command(
                "replSetStepDown",
                timeout_secs
            )
        except Exception as e:
            logger.error(f"主节点降级失败: {str(e)}")
            raise
            
    def get_server_status(self) -> Dict:
        """获取服务器状态
        
        Returns:
            Dict: 服务器状态信息
        """
        try:
            return self._client.admin.command("serverStatus")
        except Exception as e:
            logger.error(f"获取服务器状态失败: {str(e)}")
            raise
            
    def get_slow_queries(
        self,
        threshold_ms: int = 100,
        limit: int = 10
    ) -> List[Dict]:
        """获取慢查询
        
        Args:
            threshold_ms: 阈值(毫秒)
            limit: 返回记录数限制
            
        Returns:
            List[Dict]: 慢查询列表
        """
        try:
            system_profile = self._db["system.profile"]
            return list(system_profile.find({
                "millis": {"$gt": threshold_ms}
            }).sort("millis", -1).limit(limit))
        except Exception as e:
            logger.error(f"获取慢查询失败: {str(e)}")
            raise
            
    def get_collection_stats(self, collection_name: str) -> Dict:
        """获取集合统计信息
        
        Args:
            collection_name: 集合名称
            
        Returns:
            Dict: 集合统计信息
        """
        try:
            return self._db.command("collStats", collection_name)
        except Exception as e:
            logger.error(f"获取集合统计信息失败: {str(e)}")
            raise
            
    def get_operation_stats(self) -> Dict:
        """获取操作统计信息
        
        Returns:
            Dict: 操作统计信息
        """
        try:
            return self._client.admin.command("currentOp")
        except Exception as e:
            logger.error(f"获取操作统计信息失败: {str(e)}")
            raise
            
    def kill_operation(self, op_id: int) -> Dict:
        """终止操作
        
        Args:
            op_id: 操作ID
            
        Returns:
            Dict: 操作结果
        """
        try:
            return self._client.admin.command("killOp", op=op_id)
        except Exception as e:
            logger.error(f"终止操作失败: {str(e)}")
            raise 