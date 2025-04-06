"""
数据库管理命令行工具

提供数据库管理相关的命令行功能
"""
import os
import click
import json
from typing import Optional, List, Union

from .mysql_manager import MySQLManager
from .mongo_manager import MongoDBManager
from .migration_manager import MySQLMigrationManager
from .mongo_migration_manager import MongoDBMigrationManager

# 默认数据库连接URL
DEFAULT_MYSQL_URL = os.getenv("MYSQL_URL", "mysql+pymysql://root:root@localhost:3306/test")
DEFAULT_MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/test")
# 默认迁移文件目录
DEFAULT_MIGRATIONS_DIR = os.getenv("MIGRATIONS_DIR", "migrations")

# MongoDB连接池默认配置
DEFAULT_MONGO_MAX_POOL_SIZE = int(os.getenv("MONGO_MAX_POOL_SIZE", "100"))
DEFAULT_MONGO_MIN_POOL_SIZE = int(os.getenv("MONGO_MIN_POOL_SIZE", "10"))
DEFAULT_MONGO_MAX_IDLE_TIME = int(os.getenv("MONGO_MAX_IDLE_TIME", "10000"))
DEFAULT_MONGO_CONNECT_TIMEOUT = int(os.getenv("MONGO_CONNECT_TIMEOUT", "5000"))
DEFAULT_MONGO_SERVER_SELECTION_TIMEOUT = int(os.getenv("MONGO_SERVER_SELECTION_TIMEOUT", "5000"))

def get_mysql_manager(db_url: Optional[str] = None) -> MySQLManager:
    """获取MySQL管理器实例"""
    return MySQLManager(db_url or DEFAULT_MYSQL_URL)

def get_mongo_manager(
    db_url: Optional[str] = None,
    max_pool_size: Optional[int] = None,
    min_pool_size: Optional[int] = None,
    max_idle_time_ms: Optional[int] = None,
    connect_timeout_ms: Optional[int] = None,
    server_selection_timeout_ms: Optional[int] = None
) -> MongoDBManager:
    """获取MongoDB管理器实例"""
    return MongoDBManager(
        db_url or DEFAULT_MONGO_URL,
        max_pool_size=max_pool_size or DEFAULT_MONGO_MAX_POOL_SIZE,
        min_pool_size=min_pool_size or DEFAULT_MONGO_MIN_POOL_SIZE,
        max_idle_time_ms=max_idle_time_ms or DEFAULT_MONGO_MAX_IDLE_TIME,
        connect_timeout_ms=connect_timeout_ms or DEFAULT_MONGO_CONNECT_TIMEOUT,
        server_selection_timeout_ms=server_selection_timeout_ms or DEFAULT_MONGO_SERVER_SELECTION_TIMEOUT
    )

def get_migration_manager(
    db_type: str,
    db_manager: Union[MySQLManager, MongoDBManager],
    migrations_dir: Optional[str] = None
) -> Union[MySQLMigrationManager, MongoDBMigrationManager]:
    """获取迁移管理器实例"""
    migrations_dir = migrations_dir or os.path.join(DEFAULT_MIGRATIONS_DIR, db_type)
    if db_type == "mysql":
        return MySQLMigrationManager(db_manager, migrations_dir)
    else:
        return MongoDBMigrationManager(db_manager, migrations_dir)

@click.group()
def cli():
    """数据库管理工具"""
    pass

@cli.command()
@click.option('--type', 'db_type', type=click.Choice(['mysql', 'mongo']), required=True, help='数据库类型')
@click.option('--db-url', help='数据库连接URL')
def check(db_type: str, db_url: Optional[str]):
    """检查数据库连接"""
    manager = get_mysql_manager(db_url) if db_type == 'mysql' else get_mongo_manager(db_url)
    try:
        if manager.check_connection():
            click.echo("数据库连接正常")
        else:
            click.echo("数据库连接失败")
    finally:
        manager.close()

@cli.command()
@click.option('--type', 'db_type', type=click.Choice(['mysql', 'mongo']), required=True, help='数据库类型')
@click.argument('collection_name', required=False)
@click.argument('command', required=False)
@click.option('--query', help='查询语句(MySQL)或命令参数(MongoDB)')
@click.option('--db-url', help='数据库连接URL')
def execute(
    db_type: str,
    collection_name: Optional[str],
    command: Optional[str],
    query: Optional[str],
    db_url: Optional[str]
):
    """执行数据库命令
    
    MySQL: 直接执行SQL查询
    MongoDB: 指定集合名和命令(insert/find/update/delete)
    """
    if db_type == 'mysql':
        if not query:
            raise click.UsageError("MySQL操作需要提供--query参数")
        manager = get_mysql_manager(db_url)
        try:
            results = manager.execute_query(query)
            for row in results:
                click.echo(json.dumps(row, ensure_ascii=False))
        finally:
            manager.close()
    else:
        if not collection_name or not command:
            raise click.UsageError("MongoDB操作需要提供集合名和命令")
        manager = get_mongo_manager(db_url)
        try:
            data = json.loads(query) if query else None
            results = manager.execute_command(collection_name, command, data)
            for doc in results:
                click.echo(json.dumps(doc, ensure_ascii=False))
        finally:
            manager.close()

@cli.command()
@click.option('--type', 'db_type', type=click.Choice(['mysql', 'mongo']), required=True, help='数据库类型')
@click.argument('name')
@click.option('--db-url', help='数据库连接URL')
def info(db_type: str, name: str, db_url: Optional[str]):
    """获取表/集合信息"""
    if db_type == 'mysql':
        manager = get_mysql_manager(db_url)
        try:
            info = manager.get_table_info(name)
            click.echo(json.dumps(info, indent=2, ensure_ascii=False))
        finally:
            manager.close()
    else:
        manager = get_mongo_manager(db_url)
        try:
            info = manager.get_collection_info(name)
            click.echo(json.dumps(info, indent=2, ensure_ascii=False))
        finally:
            manager.close()

@cli.command()
@click.option('--type', 'db_type', type=click.Choice(['mysql', 'mongo']), required=True, help='数据库类型')
@click.option('--backup-path', required=True, help='备份文件路径')
@click.option('--tables', help='要备份的表/集合列表，用逗号分隔')
@click.option('--db-url', help='数据库连接URL')
def backup(db_type: str, backup_path: str, tables: Optional[str], db_url: Optional[str]):
    """备份数据库"""
    if db_type == 'mysql':
        manager = get_mysql_manager(db_url)
        try:
            table_list = tables.split(',') if tables else None
            manager.backup_database(backup_path, table_list)
            click.echo(f"MySQL数据库已备份到: {backup_path}")
        finally:
            manager.close()
    else:
        manager = get_mongo_manager(db_url)
        try:
            collection_list = tables.split(',') if tables else None
            manager.backup_database(backup_path, collection_list)
            click.echo(f"MongoDB数据库已备份到: {backup_path}")
        finally:
            manager.close()

@cli.command()
@click.option('--type', 'db_type', type=click.Choice(['mysql', 'mongo']), required=True, help='数据库类型')
@click.option('--backup-path', required=True, help='备份文件路径')
@click.option('--db-url', help='数据库连接URL')
def restore(db_type: str, backup_path: str, db_url: Optional[str]):
    """从备份文件恢复数据库"""
    if db_type == 'mysql':
        manager = get_mysql_manager(db_url)
        try:
            manager.restore_database(backup_path)
            click.echo("MySQL数据库恢复完成")
        finally:
            manager.close()
    else:
        manager = get_mongo_manager(db_url)
        try:
            manager.restore_database(backup_path)
            click.echo("MongoDB数据库恢复完成")
        finally:
            manager.close()

@cli.command('pool-status')
@click.option('--db-url', help='数据库连接URL')
def pool_status(db_url: Optional[str]):
    """查看MySQL连接池状态"""
    manager = get_mysql_manager(db_url)
    try:
        status = manager.get_pool_status()
        click.echo(json.dumps(status, indent=2))
    finally:
        manager.close()

@cli.command('clear-pool')
@click.option('--db-url', help='数据库连接URL')
def clear_pool(db_url: Optional[str]):
    """清理MySQL连接池"""
    manager = get_mysql_manager(db_url)
    try:
        manager.clear_pool()
        click.echo("连接池已清理")
    finally:
        manager.close()

@cli.group()
def migration():
    """数据库迁移管理"""
    pass

@migration.command('create')
@click.option('--type', 'db_type', type=click.Choice(['mysql', 'mongo']), required=True, help='数据库类型')
@click.argument('description')
@click.option('--migrations-dir', help='迁移文件目录')
@click.option('--db-url', help='数据库连接URL')
def create_migration(
    db_type: str,
    description: str,
    migrations_dir: Optional[str],
    db_url: Optional[str]
):
    """创建新的迁移文件"""
    manager = get_mysql_manager(db_url) if db_type == 'mysql' else get_mongo_manager(db_url)
    try:
        migration_manager = get_migration_manager(db_type, manager, migrations_dir)
        filepath = migration_manager.create_migration(description)
        click.echo(f"已创建迁移文件: {filepath}")
        click.echo("请编辑迁移文件，添加迁移内容")
    finally:
        manager.close()

@migration.command('status')
@click.option('--type', 'db_type', type=click.Choice(['mysql', 'mongo']), required=True, help='数据库类型')
@click.option('--migrations-dir', help='迁移文件目录')
@click.option('--db-url', help='数据库连接URL')
def migration_status(db_type: str, migrations_dir: Optional[str], db_url: Optional[str]):
    """查看迁移状态"""
    manager = get_mysql_manager(db_url) if db_type == 'mysql' else get_mongo_manager(db_url)
    try:
        migration_manager = get_migration_manager(db_type, manager, migrations_dir)
        
        # 获取当前版本
        current = migration_manager.get_current_version()
        click.echo(f"当前数据库版本: {current or '无'}")
        
        # 获取待执行的迁移
        pending = migration_manager.get_pending_migrations()
        if pending:
            click.echo("\n待执行的迁移:")
            for m in pending:
                click.echo(f"  - {m['version']}: {m['description']}")
        else:
            click.echo("\n没有待执行的迁移")
    finally:
        manager.close()

@migration.command('history')
@click.option('--type', 'db_type', type=click.Choice(['mysql', 'mongo']), required=True, help='数据库类型')
@click.option('--migrations-dir', help='迁移文件目录')
@click.option('--db-url', help='数据库连接URL')
def migration_history(db_type: str, migrations_dir: Optional[str], db_url: Optional[str]):
    """查看迁移历史"""
    manager = get_mysql_manager(db_url) if db_type == 'mysql' else get_mongo_manager(db_url)
    try:
        migration_manager = get_migration_manager(db_type, manager, migrations_dir)
        history = migration_manager.get_migration_history()
        
        if history:
            click.echo("迁移历史:")
            for record in history:
                status = "已应用" if record['is_applied'] else "已回滚"
                click.echo(
                    f"  - {record['version']}: {record['description']}\n"
                    f"    应用时间: {record['applied_at']}\n"
                    f"    状态: {status}"
                )
        else:
            click.echo("暂无迁移历史")
    finally:
        manager.close()

@migration.command('up')
@click.option('--type', 'db_type', type=click.Choice(['mysql', 'mongo']), required=True, help='数据库类型')
@click.option('--version', help='目标版本号')
@click.option('--dry-run', is_flag=True, help='仅打印将要执行的操作')
@click.option('--migrations-dir', help='迁移文件目录')
@click.option('--db-url', help='数据库连接URL')
def migrate_up(
    db_type: str,
    version: Optional[str],
    dry_run: bool,
    migrations_dir: Optional[str],
    db_url: Optional[str]
):
    """执行迁移"""
    manager = get_mysql_manager(db_url) if db_type == 'mysql' else get_mongo_manager(db_url)
    try:
        migration_manager = get_migration_manager(db_type, manager, migrations_dir)
        migration_manager.execute_migration(version, dry_run)
    finally:
        manager.close()

@migration.command('down')
@click.option('--type', 'db_type', type=click.Choice(['mysql', 'mongo']), required=True, help='数据库类型')
@click.option('--steps', type=int, default=1, help='回滚步数')
@click.option('--dry-run', is_flag=True, help='仅打印将要执行的操作')
@click.option('--migrations-dir', help='迁移文件目录')
@click.option('--db-url', help='数据库连接URL')
def migrate_down(
    db_type: str,
    steps: int,
    dry_run: bool,
    migrations_dir: Optional[str],
    db_url: Optional[str]
):
    """回滚迁移"""
    manager = get_mysql_manager(db_url) if db_type == 'mysql' else get_mongo_manager(db_url)
    try:
        migration_manager = get_migration_manager(db_type, manager, migrations_dir)
        migration_manager.rollback_migration(steps, dry_run)
    finally:
        manager.close()

@cli.group()
def mongo():
    """MongoDB高级功能"""
    pass

@mongo.command('aggregate')
@click.argument('collection_name')
@click.option('--pipeline', required=True, help='聚合管道(JSON格式)')
@click.option('--allow-disk-use', is_flag=True, help='允许使用磁盘')
@click.option('--db-url', help='数据库连接URL')
def mongo_aggregate(
    collection_name: str,
    pipeline: str,
    allow_disk_use: bool,
    db_url: Optional[str]
):
    """执行聚合操作"""
    manager = get_mongo_manager(db_url)
    try:
        pipeline_list = json.loads(pipeline)
        results = manager.aggregate(collection_name, pipeline_list, allow_disk_use)
        for doc in results:
            click.echo(json.dumps(doc, ensure_ascii=False))
    finally:
        manager.close()

@mongo.command('map-reduce')
@click.argument('collection_name')
@click.option('--map', 'map_function', required=True, help='Map函数(JavaScript)')
@click.option('--reduce', 'reduce_function', required=True, help='Reduce函数(JavaScript)')
@click.option('--output', required=True, help='输出集合名称')
@click.option('--query', help='查询条件(JSON格式)')
@click.option('--db-url', help='数据库连接URL')
def mongo_map_reduce(
    collection_name: str,
    map_function: str,
    reduce_function: str,
    output: str,
    query: Optional[str],
    db_url: Optional[str]
):
    """执行MapReduce操作"""
    manager = get_mongo_manager(db_url)
    try:
        query_dict = json.loads(query) if query else None
        results = manager.map_reduce(
            collection_name,
            map_function,
            reduce_function,
            output,
            query_dict
        )
        for doc in results:
            click.echo(json.dumps(doc, ensure_ascii=False))
    finally:
        manager.close()

@mongo.group('index')
def mongo_index():
    """MongoDB索引管理"""
    pass

@mongo_index.command('create-compound')
@click.argument('collection_name')
@click.option('--keys', required=True, help='索引键(JSON格式)')
@click.option('--unique', is_flag=True, help='是否唯一索引')
@click.option('--db-url', help='数据库连接URL')
def create_compound_index(
    collection_name: str,
    keys: str,
    unique: bool,
    db_url: Optional[str]
):
    """创建复合索引"""
    manager = get_mongo_manager(db_url)
    try:
        keys_list = [(k, v) for k, v in json.loads(keys).items()]
        index_name = manager.create_compound_index(
            collection_name,
            keys_list,
            unique=unique
        )
        click.echo(f"已创建索引: {index_name}")
    finally:
        manager.close()

@mongo_index.command('create-ttl')
@click.argument('collection_name')
@click.argument('field')
@click.option('--expiration-seconds', type=int, required=True, help='过期时间(秒)')
@click.option('--db-url', help='数据库连接URL')
def create_ttl_index(
    collection_name: str,
    field: str,
    expiration_seconds: int,
    db_url: Optional[str]
):
    """创建TTL索引"""
    manager = get_mongo_manager(db_url)
    try:
        index_name = manager.create_ttl_index(
            collection_name,
            field,
            expiration_seconds
        )
        click.echo(f"已创建TTL索引: {index_name}")
    finally:
        manager.close()

@mongo_index.command('create-geo')
@click.argument('collection_name')
@click.argument('field')
@click.option('--type', 'index_type', type=click.Choice(['2d', '2dsphere']),
              default='2dsphere', help='索引类型')
@click.option('--db-url', help='数据库连接URL')
def create_geospatial_index(
    collection_name: str,
    field: str,
    index_type: str,
    db_url: Optional[str]
):
    """创建地理空间索引"""
    manager = get_mongo_manager(db_url)
    try:
        index_name = manager.create_geospatial_index(
            collection_name,
            field,
            index_type
        )
        click.echo(f"已创建地理空间索引: {index_name}")
    finally:
        manager.close()

@mongo.group('repl')
def mongo_repl():
    """MongoDB复制集管理"""
    pass

@mongo_repl.command('init')
@click.argument('replica_set_name')
@click.option('--members', required=True, help='成员节点配置(JSON格式)')
@click.option('--db-url', help='数据库连接URL')
def init_replica_set(
    replica_set_name: str,
    members: str,
    db_url: Optional[str]
):
    """初始化复制集"""
    manager = get_mongo_manager(db_url)
    try:
        members_list = json.loads(members)
        result = manager.configure_replica_set(replica_set_name, members_list)
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        manager.close()

@mongo_repl.command('status')
@click.option('--db-url', help='数据库连接URL')
def replica_set_status(db_url: Optional[str]):
    """查看复制集状态"""
    manager = get_mongo_manager(db_url)
    try:
        status = manager.get_replica_set_status()
        click.echo(json.dumps(status, indent=2, ensure_ascii=False))
    finally:
        manager.close()

@mongo_repl.command('step-down')
@click.option('--timeout', type=int, default=60, help='超时时间(秒)')
@click.option('--db-url', help='数据库连接URL')
def step_down_primary(timeout: int, db_url: Optional[str]):
    """主节点降级"""
    manager = get_mongo_manager(db_url)
    try:
        result = manager.step_down_primary(timeout)
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        manager.close()

@mongo.group('monitor')
def mongo_monitor():
    """MongoDB监控功能"""
    pass

@mongo_monitor.command('server-status')
@click.option('--db-url', help='数据库连接URL')
def server_status(db_url: Optional[str]):
    """查看服务器状态"""
    manager = get_mongo_manager(db_url)
    try:
        status = manager.get_server_status()
        click.echo(json.dumps(status, indent=2, ensure_ascii=False))
    finally:
        manager.close()

@mongo_monitor.command('slow-queries')
@click.option('--threshold', type=int, default=100, help='阈值(毫秒)')
@click.option('--limit', type=int, default=10, help='返回记录数限制')
@click.option('--db-url', help='数据库连接URL')
def slow_queries(threshold: int, limit: int, db_url: Optional[str]):
    """查看慢查询"""
    manager = get_mongo_manager(db_url)
    try:
        queries = manager.get_slow_queries(threshold, limit)
        for query in queries:
            click.echo(json.dumps(query, indent=2, ensure_ascii=False))
    finally:
        manager.close()

@mongo_monitor.command('collection-stats')
@click.argument('collection_name')
@click.option('--db-url', help='数据库连接URL')
def collection_stats(collection_name: str, db_url: Optional[str]):
    """查看集合统计信息"""
    manager = get_mongo_manager(db_url)
    try:
        stats = manager.get_collection_stats(collection_name)
        click.echo(json.dumps(stats, indent=2, ensure_ascii=False))
    finally:
        manager.close()

@mongo_monitor.command('operations')
@click.option('--db-url', help='数据库连接URL')
def operation_stats(db_url: Optional[str]):
    """查看操作统计信息"""
    manager = get_mongo_manager(db_url)
    try:
        stats = manager.get_operation_stats()
        click.echo(json.dumps(stats, indent=2, ensure_ascii=False))
    finally:
        manager.close()

@mongo_monitor.command('kill-op')
@click.argument('op_id', type=int)
@click.option('--db-url', help='数据库连接URL')
def kill_operation(op_id: int, db_url: Optional[str]):
    """终止操作"""
    manager = get_mongo_manager(db_url)
    try:
        result = manager.kill_operation(op_id)
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        manager.close()

@mongo.group('pool')
def mongo_pool():
    """MongoDB连接池管理"""
    pass

@mongo_pool.command('status')
@click.option('--db-url', help='数据库连接URL')
def pool_status(db_url: Optional[str]):
    """查看连接池状态"""
    manager = get_mongo_manager(db_url)
    try:
        status = manager.get_pool_status()
        click.echo(json.dumps(status, indent=2, ensure_ascii=False))
    finally:
        manager.close()

@mongo.command('execute')
@click.argument('collection_name')
@click.argument('command')
@click.option('--data', help='命令参数(JSON格式)')
@click.option('--batch-size', type=int, default=1000, help='批处理大小')
@click.option('--db-url', help='数据库连接URL')
@click.option('--max-pool-size', type=int, help='最大连接池大小')
@click.option('--min-pool-size', type=int, help='最小连接池大小')
@click.option('--max-idle-time', type=int, help='最大空闲时间(毫秒)')
@click.option('--connect-timeout', type=int, help='连接超时时间(毫秒)')
@click.option('--server-selection-timeout', type=int, help='服务器选择超时时间(毫秒)')
def mongo_execute(
    collection_name: str,
    command: str,
    data: Optional[str],
    batch_size: int,
    db_url: Optional[str],
    max_pool_size: Optional[int],
    min_pool_size: Optional[int],
    max_idle_time: Optional[int],
    connect_timeout: Optional[int],
    server_selection_timeout: Optional[int]
):
    """执行MongoDB命令"""
    manager = get_mongo_manager(
        db_url,
        max_pool_size,
        min_pool_size,
        max_idle_time,
        connect_timeout,
        server_selection_timeout
    )
    try:
        data_dict = json.loads(data) if data else None
        results = manager.execute_command(
            collection_name,
            command,
            data_dict,
            batch_size
        )
        for doc in results:
            click.echo(json.dumps(doc, ensure_ascii=False))
    finally:
        manager.close()

@mongo.command('backup')
@click.option('--backup-path', required=True, help='备份文件路径')
@click.option('--collections', help='要备份的集合列表，用逗号分隔')
@click.option('--compress/--no-compress', default=True, help='是否压缩备份')
@click.option('--db-url', help='数据库连接URL')
@click.option('--max-pool-size', type=int, help='最大连接池大小')
@click.option('--min-pool-size', type=int, help='最小连接池大小')
@click.option('--max-idle-time', type=int, help='最大空闲时间(毫秒)')
@click.option('--connect-timeout', type=int, help='连接超时时间(毫秒)')
@click.option('--server-selection-timeout', type=int, help='服务器选择超时时间(毫秒)')
def mongo_backup(
    backup_path: str,
    collections: Optional[str],
    compress: bool,
    db_url: Optional[str],
    max_pool_size: Optional[int],
    min_pool_size: Optional[int],
    max_idle_time: Optional[int],
    connect_timeout: Optional[int],
    server_selection_timeout: Optional[int]
):
    """备份MongoDB数据库"""
    manager = get_mongo_manager(
        db_url,
        max_pool_size,
        min_pool_size,
        max_idle_time,
        connect_timeout,
        server_selection_timeout
    )
    try:
        collection_list = collections.split(',') if collections else None
        manager.backup_database(backup_path, collection_list, compress)
        click.echo(f"MongoDB数据库已备份到: {backup_path}")
    finally:
        manager.close()

@mongo.command('restore')
@click.option('--backup-path', required=True, help='备份文件路径')
@click.option('--db-url', help='数据库连接URL')
@click.option('--max-pool-size', type=int, help='最大连接池大小')
@click.option('--min-pool-size', type=int, help='最小连接池大小')
@click.option('--max-idle-time', type=int, help='最大空闲时间(毫秒)')
@click.option('--connect-timeout', type=int, help='连接超时时间(毫秒)')
@click.option('--server-selection-timeout', type=int, help='服务器选择超时时间(毫秒)')
def mongo_restore(
    backup_path: str,
    db_url: Optional[str],
    max_pool_size: Optional[int],
    min_pool_size: Optional[int],
    max_idle_time: Optional[int],
    connect_timeout: Optional[int],
    server_selection_timeout: Optional[int]
):
    """从备份恢复MongoDB数据库"""
    manager = get_mongo_manager(
        db_url,
        max_pool_size,
        min_pool_size,
        max_idle_time,
        connect_timeout,
        server_selection_timeout
    )
    try:
        manager.restore_database(backup_path)
        click.echo("MongoDB数据库恢复完成")
    finally:
        manager.close()

if __name__ == '__main__':
    cli() 