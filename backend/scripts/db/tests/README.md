# 数据库管理器单元测试

本目录包含了MySQL和MongoDB数据库管理器的单元测试用例。

## 目录结构

```
tests/
├── conftest.py              # pytest配置和通用fixture
├── requirements-test.txt    # 测试依赖包
├── test_mongo_manager.py    # MongoDB管理器测试
├── test_mysql_manager.py    # MySQL管理器测试
└── test_mysql_migration.py  # MySQL迁移测试
```

## 环境要求

### 基础环境
- Python 3.10+
- pytest 7.4+
- pytest-asyncio 0.21+
- pytest-cov 4.1+
- pytest-mock 3.12+

### 数据库要求
- MongoDB 5.0+
  - 需要启用副本集功能
  - 测试用户需要有管理员权限
- MySQL 8.0+
  - 需要启用二进制日志
  - 测试用户需要有SUPER权限

## 配置说明

### MongoDB测试配置
测试使用以下环境变量（可在.env文件中配置）：
```bash
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_USER=test_user
MONGO_PASSWORD=test_password
MONGO_DB=test_db
```

### MySQL测试配置
测试使用以下环境变量（可在.env文件中配置）：
```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=test_user
MYSQL_PASSWORD=test_password
MYSQL_DB=test_db
```

## 测试用例说明

### MongoDB测试用例 (test_mongo_manager.py)
1. 连接管理测试
   - 测试数据库连接建立
   - 测试连接池管理
   - 测试并发连接处理

2. 基础操作测试
   - 测试命令执行
   - 测试批量插入
   - 测试索引管理

3. 高级功能测试
   - 测试聚合操作
   - 测试MapReduce
   - 测试备份恢复

4. 运维功能测试
   - 测试监控功能
   - 测试错误处理
   - 测试重试机制

### MySQL测试用例 (test_mysql_manager.py)
1. 连接管理测试
   - 测试数据库连接建立
   - 测试连接池管理
   - 测试事务管理

2. 基础操作测试
   - 测试CRUD操作
   - 测试批量操作
   - 测试预处理语句

3. 高级功能测试
   - 测试存储过程调用
   - 测试游标操作
   - 测试批处理执行

4. 运维功能测试
   - 测试性能监控
   - 测试错误处理
   - 测试连接重试

### MySQL迁移测试 (test_mysql_migration.py)
1. 迁移管理测试
   - 测试迁移脚本执行
   - 测试版本管理
   - 测试回滚操作

2. 数据完整性测试
   - 测试数据迁移准确性
   - 测试约束维护
   - 测试索引同步

## 运行测试

### 运行所有测试
```bash
cd /path/to/project
PYTHONPATH=/path/to/project/backend pytest backend/scripts/db/tests -v
```

### 运行特定测试
```bash
# 运行MongoDB测试
pytest backend/scripts/db/tests/test_mongo_manager.py -v

# 运行MySQL测试
pytest backend/scripts/db/tests/test_mysql_manager.py -v

# 运行MySQL迁移测试
pytest backend/scripts/db/tests/test_mysql_migration.py -v
```

### 生成覆盖率报告
```bash
pytest backend/scripts/db/tests --cov=backend/scripts/db --cov-report=html
```

## 注意事项

1. 测试数据库安全
   - 所有测试都应该在测试专用数据库中进行
   - 测试完成后会自动清理测试数据
   - 不要在生产环境数据库上运行测试

2. 并发测试
   - 部分测试会创建多个数据库连接
   - 请确保数据库配置了足够的最大连接数
   - 注意监控服务器资源使用情况

3. 环境清理
   - 测试过程会自动创建和删除临时数据库对象
   - 如果测试异常中断，可能需要手动清理测试数据
   - 建议定期检查和清理测试环境

4. 性能考虑
   - 完整测试套件可能需要几分钟时间
   - 建议在专用测试环境中运行
   - 可以使用pytest的-k参数选择性运行部分测试

## 常见问题

1. 连接错误
   ```
   问题：无法连接到数据库
   解决：检查数据库服务是否运行，验证连接参数是否正确
   ```

2. 权限错误
   ```
   问题：操作被拒绝
   解决：确保测试用户有足够的权限，检查授权配置
   ```

3. 并发测试失败
   ```
   问题：并发测试偶尔失败
   解决：检查数据库最大连接数设置，可能需要调整并发测试的超时时间
   ```

## 贡献指南

1. 添加新测试
   - 遵循现有的测试命名规范
   - 确保添加了适当的文档注释
   - 包含正向和反向测试用例

2. 修改现有测试
   - 保持向后兼容性
   - 更新相关文档
   - 验证所有测试用例

3. 提交变更
   - 提供清晰的变更说明
   - 确保所有测试都能通过
   - 更新测试文档 