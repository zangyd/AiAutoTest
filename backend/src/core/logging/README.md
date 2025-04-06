# 日志记录组件

## 功能概述

日志记录组件提供统一的日志记录功能，支持多种日志记录方式和格式，适用于整个自动化测试平台的日志记录需求。

## 特性

- **多输出目标支持**
  * 文件日志记录
  * 控制台日志输出
  * 支持同时输出到多个目标

- **灵活的日志配置**
  * 可配置日志级别
  * 自定义日志格式
  * 支持JSON格式输出
  * 文件日志自动轮转

- **高级功能**
  * 性能日志记录
  * 上下文信息记录
  * 用户行为跟踪
  * 异常详细记录

- **安全特性**
  * 自动创建日志目录
  * 权限检查机制
  * 日志文件管理
  * 大小限制控制

## 使用方法

### 1. 基本使用

```python
from core.logging.logger import logger

# 记录不同级别的日志
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
logger.critical("这是一条严重错误日志")

# 带用户ID的日志记录
logger.info("用户登录成功", user_id=123)

# 带额外信息的日志记录
logger.info("API调用", user_id=123, api="/users", method="GET")
```

### 2. 性能日志记录

```python
from core.logging.logger import Logger

logger = Logger("performance")

with logger.log_performance("数据库查询"):
    # 执行数据库操作
    db.query()
```

### 3. 自定义日志记录器

```python
from core.logging.logger import Logger

# 创建自定义日志记录器
custom_logger = Logger(
    name="custom",
    log_dir="logs/custom",
    level=logging.DEBUG,
    max_bytes=5*1024*1024,  # 5MB
    backup_count=3
)

# 使用自定义日志记录器
custom_logger.info("自定义日志消息")
```

## 配置说明

### 1. 日志级别

- DEBUG: 调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误信息

### 2. 日志格式

默认日志格式包含以下信息：
- 时间戳
- 日志级别
- 日志名称
- 日志消息
- 用户ID（可选）
- 其他自定义字段

### 3. 文件配置

- 默认日志目录：`logs/`
- 日志文件命名：`{name}.log`
- 默认文件大小限制：10MB
- 默认备份文件数：5个

## 最佳实践

1. **日志级别使用建议**
   - DEBUG: 用于开发调试
   - INFO: 记录正常操作
   - WARNING: 记录潜在问题
   - ERROR: 记录错误信息
   - CRITICAL: 记录严重错误

2. **性能考虑**
   - 避免过多的DEBUG级别日志
   - 合理设置文件大小限制
   - 定期清理旧日志文件
   - 使用异步日志记录（大量日志场景）

3. **安全建议**
   - 不要记录敏感信息
   - 定期检查日志文件权限
   - 实施日志轮转策略
   - 配置适当的备份策略

## 常见问题

1. **日志文件权限问题**
   ```python
   # 确保日志目录具有正确权限
   logger = Logger(name="app", log_dir="/path/to/logs")
   ```

2. **日志文件大小控制**
   ```python
   # 设置较小的文件大小限制和更多的备份文件
   logger = Logger(
       name="app",
       max_bytes=1024*1024,  # 1MB
       backup_count=10
   )
   ```

3. **自定义日志格式**
   ```python
   # 使用自定义格式字符串
   logger = Logger(
       name="app",
       format_string="%(asctime)s [%(levelname)s] %(message)s"
   )
   ```

## 注意事项

1. 确保日志目录具有适当的写入权限
2. 合理配置日志级别，避免记录过多无用信息
3. 定期检查和清理日志文件
4. 在并发环境中注意日志文件的同步访问
5. 避免在日志中记录敏感信息

## 开发计划

- [ ] 添加异步日志记录支持
- [ ] 集成ELK日志分析
- [ ] 添加日志压缩功能
- [ ] 支持自定义日志过滤器
- [ ] 添加日志统计分析功能 