"""MySQL管理器单元测试

测试MySQL管理器的所有主要功能，包括：
- 连接管理
- SQL执行
- 事务处理
- 表结构查询
- 数据库备份和恢复
- 连接池管理
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError, DatabaseError

import sys
import os.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from db.mysql_manager import MySQLManager

# 测试配置
TEST_MYSQL_URL = "mysql+pymysql://test:Autotest%402024@localhost:3306/test_db"
TEST_BACKUP_PATH = "/tmp/mysql_backup_test"

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
def test_table(mysql_manager):
    """创建测试表并插入测试数据"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS test_users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        age INT,
        city VARCHAR(50)
    )
    """
    insert_data_sql = """
    INSERT INTO test_users (name, age, city) VALUES
    ('user1', 20, 'Beijing'),
    ('user2', 25, 'Shanghai'),
    ('user3', 30, 'Beijing')
    """
    mysql_manager.execute_query(create_table_sql)
    mysql_manager.execute_query(insert_data_sql)
    yield "test_users"
    # 清理测试数据
    mysql_manager.execute_query("DROP TABLE IF EXISTS test_users")

def test_connection(mysql_manager):
    """测试数据库连接"""
    assert mysql_manager.check_connection() is True

def test_execute_query(mysql_manager, test_table):
    """测试执行查询"""
    # 测试SELECT查询
    query = "SELECT * FROM test_users WHERE city = :city"
    params = {"city": "Beijing"}
    results = mysql_manager.execute_query(query, params)
    assert len(results) == 2
    assert all(row["city"] == "Beijing" for row in results)

    # 测试UPDATE查询
    update_query = "UPDATE test_users SET age = :age WHERE name = :name"
    update_params = {"age": 21, "name": "user1"}
    mysql_manager.execute_query(update_query, update_params)
    
    # 验证更新结果
    verify_query = "SELECT age FROM test_users WHERE name = :name"
    verify_params = {"name": "user1"}
    result = mysql_manager.execute_query(verify_query, verify_params)
    assert result[0]["age"] == 21

def test_execute_transaction(mysql_manager, test_table):
    """测试事务执行"""
    statements = [
        "UPDATE test_users SET age = :age WHERE name = :name",
        "INSERT INTO test_users (name, age, city) VALUES (:name, :age, :city)"
    ]
    params_list = [
        {"age": 22, "name": "user1"},
        {"name": "user4", "age": 35, "city": "Guangzhou"}
    ]
    
    # 执行事务
    mysql_manager.execute_transaction(statements, params_list)
    
    # 验证事务结果
    results = mysql_manager.execute_query("SELECT * FROM test_users")
    assert len(results) == 4
    assert any(row["name"] == "user4" and row["age"] == 35 for row in results)

def test_transaction_rollback(mysql_manager, test_table):
    """测试事务回滚"""
    statements = [
        "UPDATE test_users SET age = :age WHERE name = :name",
        "INSERT INTO test_users (invalid_column) VALUES (:value)"  # 这会导致错误
    ]
    params_list = [
        {"age": 22, "name": "user1"},
        {"value": "test"}
    ]
    
    # 执行事务应该失败并回滚
    with pytest.raises(SQLAlchemyError):
        mysql_manager.execute_transaction(statements, params_list)
    
    # 验证数据没有被修改
    results = mysql_manager.execute_query(
        "SELECT age FROM test_users WHERE name = :name",
        {"name": "user1"}
    )
    assert results[0]["age"] == 20

def test_get_table_info(mysql_manager, test_table):
    """测试获取表结构信息"""
    table_info = mysql_manager.get_table_info(test_table)
    
    # 验证表结构信息
    assert "columns" in table_info
    assert "primary_keys" in table_info
    assert "indexes" in table_info
    assert "foreign_keys" in table_info
    
    # 验证列信息
    columns = {col["name"]: col for col in table_info["columns"]}
    assert "id" in columns
    assert "name" in columns
    assert "age" in columns
    assert "city" in columns
    
    # 验证主键信息
    assert table_info["primary_keys"]["constrained_columns"] == ["id"]

@patch("subprocess.run")
def test_backup_restore(mock_run, mysql_manager):
    """测试备份和恢复"""
    # 测试备份
    mysql_manager.backup_database(TEST_BACKUP_PATH)
    mock_run.assert_called()
    
    # 测试恢复
    mysql_manager.restore_database(TEST_BACKUP_PATH)
    mock_run.assert_called()

def test_pool_management(mysql_manager):
    """测试连接池管理"""
    # 获取连接池状态
    status = mysql_manager.get_pool_status()
    assert "total_connections" in status
    assert "active_connections" in status
    assert "idle_connections" in status
    assert "reconnect_count" in status
    assert "overflow_count" in status
    
    # 测试清理连接池
    mysql_manager.clear_pool()
    status = mysql_manager.get_pool_status()
    assert status["active_connections"] == 0

def test_error_handling(mysql_manager):
    """测试错误处理"""
    # 测试无效的SQL语句
    with pytest.raises(SQLAlchemyError):
        mysql_manager.execute_query("SELECT * FROM nonexistent_table")
    
    # 测试无效的参数
    with pytest.raises(SQLAlchemyError):
        mysql_manager.execute_query(
            "SELECT * FROM test_users WHERE id = :id",
            {"invalid_param": 1}
        )

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 