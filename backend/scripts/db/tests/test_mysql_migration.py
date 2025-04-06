"""MySQL迁移管理器单元测试

测试MySQL迁移管理器的所有主要功能，包括：
- 迁移文件管理
- 版本控制
- 迁移执行
- 迁移回滚
- 迁移历史查询
"""

import os
import json
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from ..mysql_manager import MySQLManager
from ..migration_manager import MySQLMigrationManager

# 测试配置
TEST_MYSQL_URL = "mysql+pymysql://test:Autotest%402024@localhost:3306/test_db"
TEST_MIGRATIONS_DIR = "/tmp/mysql_migrations_test"

@pytest.fixture
def mysql_manager():
    """创建MySQL管理器实例"""
    manager = MySQLManager(
        TEST_MYSQL_URL,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True
    )
    yield manager
    manager.close()

@pytest.fixture
def migration_manager(mysql_manager):
    """创建迁移管理器实例"""
    # 清理环境
    mysql_manager.execute_query("DROP TABLE IF EXISTS db_version")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test1")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test2")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test_execute")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test_rollback")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test_dry_run")
    mysql_manager.execute_query("DROP TABLE IF EXISTS 迁移1")
    mysql_manager.execute_query("DROP TABLE IF EXISTS 迁移2")
    mysql_manager.execute_query("DROP TABLE IF EXISTS 迁移3")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test_version_1")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test_version_2")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test_version_3")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test_applied")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test_intermediate_1")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test_intermediate_2")
    mysql_manager.execute_query("DROP TABLE IF EXISTS test_intermediate_3")
    
    manager = MySQLMigrationManager(mysql_manager, TEST_MIGRATIONS_DIR)
    yield manager
    # 清理测试目录
    if os.path.exists(TEST_MIGRATIONS_DIR):
        for root, dirs, files in os.walk(TEST_MIGRATIONS_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(TEST_MIGRATIONS_DIR)

def test_ensure_migrations_dir(migration_manager):
    """测试确保迁移目录存在"""
    assert os.path.exists(TEST_MIGRATIONS_DIR)

def test_ensure_version_table(mysql_manager, migration_manager):
    """测试确保版本表存在"""
    # 检查版本表是否存在
    result = mysql_manager.execute_query(
        "SHOW TABLES LIKE 'db_version'"
    )
    assert len(result) > 0

def test_create_migration(migration_manager):
    """测试创建迁移文件"""
    description = "创建用户表"
    filepath = migration_manager.create_migration(description)
    
    # 验证文件是否创建
    assert os.path.exists(filepath)
    
    # 验证文件内容
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)
        assert "version" in content
        assert content["description"] == description
        assert "up" in content
        assert "down" in content

def test_get_current_version(migration_manager):
    """测试获取当前版本"""
    # 初始状态应该没有版本
    assert migration_manager.get_current_version() is None
    
    # 创建并应用一个迁移
    description = "测试迁移"
    filepath = migration_manager.create_migration(description)
    
    # 修改迁移文件内容
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)
    content["up"] = ["CREATE TABLE test (id INT PRIMARY KEY)"]
    content["down"] = ["DROP TABLE IF EXISTS test"]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(content, f)
    
    # 执行迁移
    migration_manager.execute_migration()
    
    # 验证当前版本
    current_version = migration_manager.get_current_version()
    assert current_version is not None
    assert current_version == content["version"]

def test_get_pending_migrations(migration_manager):
    """测试获取待执行的迁移"""
    # 创建两个迁移文件
    migration1 = migration_manager.create_migration("迁移1")
    migration2 = migration_manager.create_migration("迁移2")
    
    # 获取待执行的迁移
    pending = migration_manager.get_pending_migrations()
    assert len(pending) == 2
    
    # 执行第一个迁移
    with open(migration1, 'r', encoding='utf-8') as f:
        content = json.load(f)
    content["up"] = ["CREATE TABLE test1 (id INT PRIMARY KEY)"]
    content["down"] = ["DROP TABLE IF EXISTS test1"]
    with open(migration1, 'w', encoding='utf-8') as f:
        json.dump(content, f)
        
    # 修改第二个迁移文件
    with open(migration2, 'r', encoding='utf-8') as f:
        content2 = json.load(f)
    content2["up"] = ["CREATE TABLE test2 (id INT PRIMARY KEY)"]
    content2["down"] = ["DROP TABLE IF EXISTS test2"]
    with open(migration2, 'w', encoding='utf-8') as f:
        json.dump(content2, f)
        
    # 执行所有迁移
    migration_manager.execute_migration()
    
    # 再次获取待执行的迁移
    pending = migration_manager.get_pending_migrations()
    assert len(pending) == 0  # 所有迁移都已执行，应该没有待执行的迁移

def test_execute_migration(migration_manager):
    """测试执行迁移"""
    # 创建测试迁移
    filepath = migration_manager.create_migration("创建测试表")
    
    # 修改迁移文件内容
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)
    content["up"] = [
        "CREATE TABLE test_execute (id INT PRIMARY KEY, name VARCHAR(50))",
        "INSERT INTO test_execute VALUES (1, 'test')"
    ]
    content["down"] = ["DROP TABLE IF EXISTS test_execute"]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(content, f)
    
    # 执行迁移
    migration_manager.execute_migration()
    
    # 验证迁移是否成功执行
    result = migration_manager.mysql_manager.execute_query(
        "SELECT * FROM test_execute"
    )
    assert len(result) == 1
    assert result[0]["name"] == "test"

def test_rollback_migration(migration_manager):
    """测试回滚迁移"""
    # 创建并执行测试迁移
    filepath = migration_manager.create_migration("创建回滚测试表")
    
    # 修改迁移文件内容
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)
    content["up"] = ["CREATE TABLE test_rollback (id INT PRIMARY KEY)"]
    content["down"] = ["DROP TABLE IF EXISTS test_rollback"]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(content, f)
    
    # 执行迁移
    migration_manager.execute_migration()
    
    # 验证表是否创建
    result = migration_manager.mysql_manager.execute_query(
        "SHOW TABLES LIKE 'test_rollback'"
    )
    assert len(result) > 0
    
    # 回滚迁移
    migration_manager.rollback_migration()
    
    # 验证表是否被删除
    result = migration_manager.mysql_manager.execute_query(
        "SHOW TABLES LIKE 'test_rollback'"
    )
    assert len(result) == 0

def test_migration_history(migration_manager):
    """测试迁移历史"""
    # 创建并执行多个迁移
    descriptions = ["迁移1", "迁移2", "迁移3"]
    migrations = []
    for desc in descriptions:
        filepath = migration_manager.create_migration(desc)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = json.load(f)
        content["up"] = [f"CREATE TABLE {desc} (id INT PRIMARY KEY)"]
        content["down"] = [f"DROP TABLE IF EXISTS {desc}"]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f)
        migrations.append(content)
        
    # 按顺序执行迁移
    for migration in migrations:
        migration_manager.execute_migration()
    
    # 获取迁移历史
    history = migration_manager.get_migration_history()
    assert len(history) == 3
    assert all(h["description"] in descriptions for h in history)

def test_dry_run(migration_manager):
    """测试演练模式"""
    # 创建测试迁移
    filepath = migration_manager.create_migration("演练测试")
    
    # 修改迁移文件内容
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)
    content["up"] = ["CREATE TABLE test_dry_run (id INT PRIMARY KEY)"]
    content["down"] = ["DROP TABLE IF EXISTS test_dry_run"]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(content, f)
    
    # 执行演练
    migration_manager.execute_migration(dry_run=True)
    
    # 验证表未被创建
    result = migration_manager.mysql_manager.execute_query(
        "SHOW TABLES LIKE 'test_dry_run'"
    )
    assert len(result) == 0

def test_execute_specific_version(migration_manager):
    """测试执行指定版本的迁移"""
    # 创建三个迁移文件
    migrations = []
    for i in range(3):
        filepath = migration_manager.create_migration(f"测试迁移{i+1}")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = json.load(f)
        content["up"] = [f"CREATE TABLE test_version_{i+1} (id INT PRIMARY KEY)"]
        content["down"] = [f"DROP TABLE IF EXISTS test_version_{i+1}"]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f)
        migrations.append(content)
    
    # 执行到第二个版本
    target_version = migrations[1]["version"]
    migration_manager.execute_migration(version=target_version)
    
    # 验证只有前两个表被创建
    for i in range(1, 3):
        result = migration_manager.mysql_manager.execute_query(
            f"SHOW TABLES LIKE 'test_version_{i}'"
        )
        assert len(result) > 0 if i <= 2 else len(result) == 0
    
    # 验证当前版本是目标版本
    assert migration_manager.get_current_version() == target_version

def test_execute_invalid_version(migration_manager):
    """测试执行无效版本的迁移"""
    # 创建一个迁移文件
    filepath = migration_manager.create_migration("测试迁移")
    
    # 尝试执行一个不存在的版本
    invalid_version = "invalid_version_20240101"
    with pytest.raises(ValueError) as excinfo:
        migration_manager.execute_migration(version=invalid_version)
    assert "无效的目标版本" in str(excinfo.value)

def test_execute_already_applied_version(migration_manager):
    """测试执行已应用版本的迁移"""
    # 创建并执行一个迁移
    filepath = migration_manager.create_migration("已应用的迁移")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)
    content["up"] = ["CREATE TABLE test_applied (id INT PRIMARY KEY)"]
    content["down"] = ["DROP TABLE IF EXISTS test_applied"]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(content, f)
    
    # 第一次执行迁移
    migration_manager.execute_migration()
    applied_version = migration_manager.get_current_version()
    
    # 再次执行同一版本
    migration_manager.execute_migration(version=applied_version)
    
    # 验证版本没有变化
    assert migration_manager.get_current_version() == applied_version

def test_execute_intermediate_version(migration_manager):
    """测试在多版本迁移中执行中间版本"""
    # 创建三个迁移文件
    migrations = []
    for i in range(3):
        filepath = migration_manager.create_migration(f"中间版本测试{i+1}")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = json.load(f)
        content["up"] = [f"CREATE TABLE test_intermediate_{i+1} (id INT PRIMARY KEY)"]
        content["down"] = [f"DROP TABLE IF EXISTS test_intermediate_{i+1}"]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f)
        migrations.append(content)
    
    # 先执行到最新版本
    migration_manager.execute_migration()
    
    # 回滚到第二个版本
    target_version = migrations[1]["version"]
    migration_manager.rollback_migration(target_version)
    
    # 验证只有前两个表存在
    for i in range(1, 4):
        result = migration_manager.mysql_manager.execute_query(
            f"SHOW TABLES LIKE 'test_intermediate_{i}'"
        )
        assert len(result) > 0 if i <= 2 else len(result) == 0
    
    # 验证当前版本是目标版本
    assert migration_manager.get_current_version() == target_version

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 