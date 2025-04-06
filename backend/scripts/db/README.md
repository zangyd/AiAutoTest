# 数据库管理工具

这是一个功能强大的数据库管理工具包，提供了完整的数据库操作、迁移管理和连接池管理功能。支持MySQL关系型数据库和MongoDB文档数据库。

## 功能特性

- 数据库连接管理
  - 支持连接池配置
  - 自动连接健康检查
  - 连接池状态监控
  - 智能连接回收机制
  - 连接重试机制
  - 连接池自动清理

- MySQL数据库操作
  - SQL查询执行（支持SELECT和非SELECT语句）
  - 事务管理（支持自动提交和回滚）
  - 数据库备份/恢复（支持表级别操作）
  - 表结构信息查询
  - 索引管理
  - DDL语句支持
  - 批量操作支持
  - 参数化查询
  - 结果集映射

- MongoDB数据库操作
  - 文档CRUD操作
  - 聚合查询
  - 索引管理
  - 集合统计
  - 数据库备份/恢复
  - 批量操作
  - 事务支持
  - 复制集支持

- 数据库迁移
  - 版本管理
  - 迁移文件创建
  - 迁移执行/回滚
  - 迁移历史查询
  - 依赖检查
  - 并发控制

## 安装要求

- Python 3.10+
- SQLAlchemy 2.0+
- PyMySQL
- pymongo
- Click
- cryptography（用于MySQL密码认证）

## 快速开始

1. 设置环境变量:
```bash
# MySQL连接
export MYSQL_URL="mysql+pymysql://user:password@localhost:3306/dbname"
export MYSQL_POOL_SIZE=5
export MYSQL_MAX_OVERFLOW=10
export MYSQL_POOL_TIMEOUT=30
export MYSQL_POOL_RECYCLE=3600

# MongoDB连接
export MONGODB_URL="mongodb://user:password@localhost:27017/dbname"
export MONGODB_MAX_POOL_SIZE=50
export MONGODB_MIN_POOL_SIZE=10
export MONGODB_MAX_IDLE_TIME_MS=10000
```

2. 检查数据库连接:
```bash
# 检查MySQL连接
python -m backend.scripts.db check --type mysql

# 检查MongoDB连接
python -m backend.scripts.db check --type mongodb
```

## 命令行工具使用

### MySQL数据库操作

1. 检查数据库连接:
```bash
# 基本连接检查
python -m backend.scripts.db check --type mysql --db-url "mysql+pymysql://user:password@localhost:3306/dbname"

# 带连接池配置的检查
python -m backend.scripts.db check --type mysql \
    --db-url "mysql+pymysql://user:password@localhost:3306/dbname" \
    --pool-size 5 \
    --max-overflow 10 \
    --pool-timeout 30 \
    --pool-recycle 3600
```

2. 查看表信息:
```bash
# 查看表结构
python -m backend.scripts.db info --type mysql table_name

# 查看表统计信息
python -m backend.scripts.db info --type mysql table_name --stats

# 查看表索引信息
python -m backend.scripts.db info --type mysql table_name --indexes

# 导出表结构
python -m backend.scripts.db info --type mysql table_name --export schema.json
```

3. 执行SQL:
```bash
# 执行SELECT查询
python -m backend.scripts.db execute --type mysql "SELECT * FROM users WHERE age > 18"

# 执行带参数的查询
python -m backend.scripts.db execute --type mysql \
    "SELECT * FROM users WHERE age > :age" \
    --params '{"age": 18}'

# 执行INSERT语句
python -m backend.scripts.db execute --type mysql \
    "INSERT INTO users (name, age) VALUES (:name, :age)" \
    --params '{"name": "张三", "age": 25}'

# 执行多条语句（事务）
python -m backend.scripts.db execute --type mysql \
    --file statements.sql \
    --transaction
```

4. 数据库备份/恢复:
```bash
# 完整备份
python -m backend.scripts.db backup --type mysql \
    --backup-path /path/to/backup.sql

# 指定表备份
python -m backend.scripts.db backup --type mysql \
    --backup-path /path/to/backup.sql \
    --tables users orders

# 带WHERE条件的备份
python -m backend.scripts.db backup --type mysql \
    --backup-path /path/to/backup.sql \
    --tables users \
    --where "created_at > '2024-01-01'"

# 恢复数据库
python -m backend.scripts.db restore --type mysql \
    --backup-path /path/to/backup.sql

# 恢复指定表
python -m backend.scripts.db restore --type mysql \
    --backup-path /path/to/backup.sql \
    --tables users orders
```

5. 连接池管理:
```bash
# 查看连接池状态
python -m backend.scripts.db pool-status --type mysql

# 查看详细统计信息
python -m backend.scripts.db pool-status --type mysql --stats

# 清理连接池
python -m backend.scripts.db clear-pool --type mysql

# 重置连接池
python -m backend.scripts.db reset-pool --type mysql
```

### MongoDB数据库操作

1. 检查数据库连接:
```bash
# 基本连接检查
python -m backend.scripts.db check --type mongodb \
    --db-url "mongodb://user:password@localhost:27017/dbname"

# 带连接池配置的检查
python -m backend.scripts.db check --type mongodb \
    --db-url "mongodb://user:password@localhost:27017/dbname" \
    --max-pool-size 50 \
    --min-pool-size 10 \
    --max-idle-time-ms 10000
```

2. 查看集合信息:
```bash
# 查看集合信息
python -m backend.scripts.db info --type mongodb collection_name

# 查看集合统计
python -m backend.scripts.db info --type mongodb collection_name --stats

# 查看集合索引
python -m backend.scripts.db info --type mongodb collection_name --indexes

# 导出集合信息
python -m backend.scripts.db info --type mongodb collection_name --export schema.json
```

3. 执行查询:
```bash
# 基本查询
python -m backend.scripts.db execute --type mongodb \
    --collection users \
    --query '{"age": {"$gt": 18}}'

# 聚合查询
python -m backend.scripts.db execute --type mongodb \
    --collection users \
    --aggregate '[{"$match": {"age": {"$gt": 18}}}, {"$group": {"_id": "$city", "count": {"$sum": 1}}}]'

# 更新操作
python -m backend.scripts.db execute --type mongodb \
    --collection users \
    --update '{"$set": {"status": "active"}}' \
    --query '{"age": {"$gt": 18}}'

# 删除操作
python -m backend.scripts.db execute --type mongodb \
    --collection users \
    --delete \
    --query '{"status": "inactive"}'
```

### 数据库迁移

1. 创建新迁移:
```bash
# MySQL迁移
python -m backend.scripts.db create --type mysql \
    --description "创建用户表" \
    --up up.sql \
    --down down.sql

# MongoDB迁移
python -m backend.scripts.db create --type mongodb \
    --description "创建用户集合" \
    --up up.js \
    --down down.js
```

2. 执行迁移:
```bash
# 执行所有待迁移
python -m backend.scripts.db migrate --type mysql

# 执行指定步数
python -m backend.scripts.db migrate --type mysql --steps 2

# 执行到指定版本
python -m backend.scripts.db migrate --type mysql --version "20240401_001"
```

3. 回滚迁移:
```bash
# 回滚最后一次迁移
python -m backend.scripts.db rollback --type mysql

# 回滚指定步数
python -m backend.scripts.db rollback --type mysql --steps 2

# 回滚到指定版本
python -m backend.scripts.db rollback --type mysql --version "20240401_001"
```

4. 查看迁移历史:
```bash
# 查看所有历史
python -m backend.scripts.db history --type mysql

# 查看最近N条历史
python -m backend.scripts.db history --type mysql --limit 10

# 导出迁移历史
python -m backend.scripts.db history --type mysql --export history.json
```

## 在代码中使用

### MySQL操作示例

```python
from backend.scripts.db import MySQLManager

# 创建MySQL管理器实例
mysql_manager = MySQLManager(
    db_url="mysql+pymysql://user:password@localhost:3306/dbname",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)

# 执行SELECT查询
results = mysql_manager.execute_query(
    "SELECT * FROM users WHERE age > :age",
    {"age": 18}
)

# 执行INSERT/UPDATE/DELETE
mysql_manager.execute_query(
    "INSERT INTO users (name, age) VALUES (:name, :age)",
    {"name": "张三", "age": 25}
)

# 执行事务
statements = [
    "INSERT INTO users (name, age) VALUES (:name, :age)",
    "UPDATE user_stats SET total = total + 1"
]
params_list = [
    {"name": "张三", "age": 25},
    {}
]
mysql_manager.execute_transaction(statements, params_list)

# 获取表信息
table_info = mysql_manager.get_table_info("users")

# 备份数据库
mysql_manager.backup_database(
    backup_path="/path/to/backup.sql",
    tables=["users", "orders"]
)

# 还原数据库
mysql_manager.restore_database(
    backup_path="/path/to/backup.sql"
)

# 获取连接池状态
pool_status = mysql_manager.get_pool_status()

# 清理连接池
mysql_manager.clear_pool()
```

### MongoDB操作示例

```python
from backend.scripts.db import MongoDBManager

# 创建MongoDB管理器实例
mongodb_manager = MongoDBManager(
    db_url="mongodb://user:password@localhost:27017/dbname",
    max_pool_size=50,
    min_pool_size=10,
    max_idle_time_ms=10000
)

# 插入文档
mongodb_manager.insert_one("users", {
    "name": "张三",
    "age": 25,
    "city": "北京"
})

# 批量插入
documents = [
    {"name": "张三", "age": 25},
    {"name": "李四", "age": 30}
]
mongodb_manager.insert_many("users", documents)

# 查询文档
results = mongodb_manager.find(
    "users",
    {"age": {"$gt": 18}},
    sort=[("age", 1)],
    limit=10
)

# 聚合查询
pipeline = [
    {"$match": {"age": {"$gt": 18}}},
    {"$group": {"_id": "$city", "count": {"$sum": 1}}}
]
results = mongodb_manager.aggregate("users", pipeline)

# 更新文档
mongodb_manager.update_many(
    "users",
    {"age": {"$gt": 18}},
    {"$set": {"status": "active"}}
)

# 删除文档
mongodb_manager.delete_many(
    "users",
    {"status": "inactive"}
)

# 创建索引
mongodb_manager.create_index(
    "users",
    [("age", 1), ("city", 1)],
    unique=True
)

# 获取集合统计
stats = mongodb_manager.get_collection_stats("users")
```

## 错误处理

工具包提供了完善的错误处理机制：

1. 数据库连接错误
```python
try:
    mysql_manager.execute_query("SELECT * FROM users")
except ConnectionError as e:
    print(f"数据库连接失败: {e}")
```

2. SQL语法错误
```python
try:
    mysql_manager.execute_query("INVALID SQL")
except SQLSyntaxError as e:
    print(f"SQL语法错误: {e}")
```

3. 事务错误
```python
try:
    mysql_manager.execute_transaction(statements, params_list)
except TransactionError as e:
    print(f"事务执行失败: {e}")
```

4. 备份/还原错误
```python
try:
    mysql_manager.backup_database("/invalid/path/backup.sql")
except BackupError as e:
    print(f"备份失败: {e}")
```

## 最佳实践

1. 连接池配置
- 根据应用负载调整池大小
- 设置合理的超时时间
- 启用连接健康检查
- 定期清理空闲连接

2. 事务管理
- 合理使用事务边界
- 避免长事务
- 正确处理事务回滚
- 使用参数化查询

3. 性能优化
- 合理使用索引
- 优化查询语句
- 控制结果集大小
- 使用批量操作

4. 安全性
- 使用参数化查询防止SQL注入
- 妥善保管数据库凭证
- 定期备份重要数据
- 控制访问权限

5. 监控和维护
- 监控连接池状态
- 及时清理无用连接
- 定期检查性能指标
- 保持日志记录完整

### 数据库迁移管理

#### 目录结构

```
backend/scripts/db/
├── migrations/           # 迁移文件目录
│   └── *.json           # 迁移文件（JSON格式）
├── migration_manager.py  # 迁移管理器
└── mysql_manager.py     # MySQL管理器
```

#### 迁移文件格式

迁移文件采用JSON格式，命名规则为：`{version}_{description}.json`
- version: 版本号，格式为YYYYMMDDHHMMSSnn（年月日时分秒+2位计数器）
- description: 迁移描述（中文或英文）

文件内容结构：
```json
{
  "version": "20240406120001",        // 迁移版本号
  "description": "迁移描述",          // 迁移说明
  "up": [                             // 升级SQL语句数组
    "SQL语句1",
    "SQL语句2"
  ],
  "down": [                           // 回滚SQL语句数组
    "SQL语句1",
    "SQL语句2"
  ]
}
```

#### 迁移命令

1. 创建迁移:
```bash
# 创建新的迁移文件
python -m backend.scripts.db migration create "迁移描述"

# 指定迁移目录创建
python -m backend.scripts.db migration create "迁移描述" --dir /path/to/migrations
```

2. 执行迁移:
```bash
# 执行所有待处理的迁移
python -m backend.scripts.db migration up

# 执行到指定版本
python -m backend.scripts.db migration up --version 20240406120001

# 回滚最近一次迁移
python -m backend.scripts.db migration down

# 回滚到指定版本
python -m backend.scripts.db migration down --version 20240406120001

# 重新执行指定版本
python -m backend.scripts.db migration redo --version 20240406120001
```

3. 查看迁移状态:
```bash
# 查看迁移历史
python -m backend.scripts.db migration history

# 查看待处理迁移
python -m backend.scripts.db migration pending

# 查看当前版本
python -m backend.scripts.db migration current

# 验证迁移文件
python -m backend.scripts.db migration validate
```

4. 迁移管理:
```bash
# 初始化迁移环境
python -m backend.scripts.db migration init

# 清理迁移历史
python -m backend.scripts.db migration clean

# 修复迁移状态
python -m backend.scripts.db migration repair
```

#### 最佳实践

1. 版本号管理
   - 使用时间戳+2位计数器确保唯一性
   - 按时间顺序执行迁移
   - 不允许修改已执行的迁移文件

2. SQL编写规范
   - 使用完整的SQL语句
   - 处理好依赖关系
   - 提供回滚操作
   - 注意SQL兼容性

3. 迁移策略
   - 小步迭代，避免大规模变更
   - 保持向后兼容
   - 先在测试环境验证
   - 做好备份和恢复预案

4. 安全考虑
   - 控制迁移文件权限
   - 敏感数据加密存储
   - 记录迁移操作日志
   - 设置迁移超时限制 