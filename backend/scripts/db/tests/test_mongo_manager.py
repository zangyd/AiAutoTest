"""MongoDB管理器单元测试

测试MongoDB管理器的所有主要功能，包括：
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
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from ..mongo_manager import MongoDBManager, retry_on_error
from pymongo.errors import (
    OperationFailure,
    NetworkTimeout,
    ConnectionFailure,
    ServerSelectionTimeoutError
)

# 测试配置
TEST_MONGO_URL = "mongodb://test_user:test_password@localhost:27017/test_db?authSource=admin"
TEST_BACKUP_PATH = "/tmp/mongo_backup_test"

@pytest.fixture
def mongo_manager():
    """创建MongoDB管理器实例"""
    manager = MongoDBManager(
        TEST_MONGO_URL,
        max_pool_size=10,
        min_pool_size=1,
        max_idle_time_ms=1000,
        connect_timeout_ms=1000,
        server_selection_timeout_ms=1000
    )
    yield manager
    manager.close()

@pytest.fixture
def test_collection(mongo_manager):
    """创建测试集合并插入测试数据"""
    collection_name = "test_collection"
    test_data = [
        {"name": "user1", "age": 20, "city": "Beijing"},
        {"name": "user2", "age": 25, "city": "Shanghai"},
        {"name": "user3", "age": 30, "city": "Beijing"}
    ]
    mongo_manager.execute_command(collection_name, "insert", test_data)
    yield collection_name
    # 清理测试数据
    mongo_manager.execute_command(collection_name, "delete", {})

def test_connection(mongo_manager):
    """测试数据库连接"""
    assert mongo_manager.check_connection() is True

def test_execute_command(mongo_manager, test_collection):
    """测试执行命令"""
    # 测试查询
    results = mongo_manager.execute_command(test_collection, "find", {"city": "Beijing"})
    assert len(results) == 2
    assert all(doc["city"] == "Beijing" for doc in results)

    # 测试更新
    update_data = {
        "filter": {"name": "user1"},
        "update": {"$set": {"age": 21}}
    }
    results = mongo_manager.execute_command(test_collection, "update", update_data)
    assert results[0]["modified_count"] == 1

    # 测试删除
    results = mongo_manager.execute_command(test_collection, "delete", {"name": "user1"})
    assert results[0]["deleted_count"] == 1

def test_batch_insert(mongo_manager):
    """测试批量插入"""
    collection_name = "test_batch"
    # 生成大量测试数据
    test_data = [{"index": i} for i in range(2000)]
    
    results = mongo_manager.execute_command(collection_name, "insert", test_data, batch_size=500)
    total_inserted = sum(len(r["inserted_ids"]) for r in results)
    assert total_inserted == 2000

    # 清理测试数据
    mongo_manager.execute_command(collection_name, "delete", {})

def test_index_management(mongo_manager, test_collection):
    """测试索引管理"""
    # 测试复合索引
    index_name = mongo_manager.create_compound_index(
        test_collection,
        [("name", 1), ("age", -1)],
        unique=True
    )
    assert index_name == "name_1_age_-1"

    # 测试TTL索引
    ttl_index = mongo_manager.create_ttl_index(
        test_collection,
        "created_at",
        3600  # 1小时过期
    )
    assert ttl_index == "created_at_1"

    # 测试地理空间索引
    geo_index = mongo_manager.create_geospatial_index(
        test_collection,
        "location"
    )
    assert geo_index == "location_2dsphere"

def test_aggregation(mongo_manager, test_collection):
    """测试聚合操作"""
    pipeline = [
        {"$group": {
            "_id": "$city",
            "count": {"$sum": 1},
            "avg_age": {"$avg": "$age"}
        }}
    ]
    results = mongo_manager.aggregate(test_collection, pipeline)
    assert len(results) > 0
    assert all("count" in doc and "avg_age" in doc for doc in results)

def test_map_reduce(mongo_manager, test_collection):
    """测试MapReduce操作"""
    map_func = "function() { emit(this.city, 1); }"
    reduce_func = "function(key, values) { return Array.sum(values); }"
    
    results = mongo_manager.map_reduce(
        test_collection,
        map_func,
        reduce_func,
        "city_counts"
    )
    assert len(results) > 0

@patch("subprocess.run")
def test_backup_restore(mock_run, mongo_manager):
    """测试备份和恢复"""
    # 测试备份
    mongo_manager.backup_database(TEST_BACKUP_PATH, compress=True)
    mock_run.assert_called()
    
    # 测试恢复
    mongo_manager.restore_database(TEST_BACKUP_PATH)
    mock_run.assert_called()

def test_retry_decorator():
    """测试重试装饰器"""
    mock_func = MagicMock(side_effect=[
        NetworkTimeout("连接超时"),
        ConnectionFailure("连接失败"),
        "success"
    ])
    
    @retry_on_error(retries=3, delay=0.1)
    def test_func():
        return mock_func()
        
    result = test_func()
    assert result == "success"
    assert mock_func.call_count == 3

def test_pool_management(mongo_manager):
    """测试连接池管理"""
    status = mongo_manager.get_pool_status()
    assert "max_pool_size" in status
    assert "min_pool_size" in status
    assert "max_idle_time_ms" in status
    assert "active_connections" in status

@pytest.mark.asyncio
async def test_concurrent_operations(mongo_manager, test_collection):
    """测试并发操作"""
    import asyncio
    
    async def concurrent_find():
        return mongo_manager.execute_command(test_collection, "find", {})
    
    # 并发执行10个查询
    tasks = [concurrent_find() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    assert all(len(r) > 0 for r in results)

def test_error_handling(mongo_manager):
    """测试错误处理"""
    with pytest.raises(ValueError):
        mongo_manager.execute_command("test", "invalid_command", {})
        
    with pytest.raises(OperationFailure):
        # 尝试在不存在的数据库上执行操作
        invalid_manager = MongoDBManager("mongodb://localhost:27017/nonexistent_db")
        invalid_manager.execute_command("test", "find", {"$invalid": 1})

def test_monitoring(mongo_manager, test_collection):
    """测试监控功能"""
    collection_name = test_collection  # 获取集合名称字符串
    
    # 测试服务器状态
    status = mongo_manager.get_server_status()
    assert "connections" in status
    
    # 测试慢查询
    queries = mongo_manager.get_slow_queries(threshold_ms=0, limit=5)
    assert isinstance(queries, list)
    
    # 测试集合统计
    stats = mongo_manager.get_collection_stats(collection_name)
    assert "size" in stats
    assert "count" in stats
    
    # 测试操作统计
    op_stats = mongo_manager.get_operation_stats()
    assert "inprog" in op_stats

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 