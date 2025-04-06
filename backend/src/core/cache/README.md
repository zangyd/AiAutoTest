# Redis缓存管理工具

## 功能概述

Redis缓存管理工具提供了一个统一的缓存操作接口，支持异步操作，具有以下核心功能：

- 键前缀管理
- 过期时间管理
- 批量操作支持
- 分布式锁机制
- 缓存装饰器
- JSON序列化支持

## 特性

- 异步操作：基于`redis.asyncio.Redis`实现异步操作
- 类型安全：完整的类型注解支持
- 错误处理：完善的异常处理机制
- 可扩展性：支持自定义JSON编解码器
- 使用简单：统一的API接口设计

## 安装依赖

```bash
pip install redis python-dotenv
```

## 基本配置

在项目的`.env`文件中配置Redis连接信息：

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password
```

## 使用示例

### 1. 初始化缓存管理器

```python
from redis.asyncio import Redis
from core.cache import CacheManager

# 创建Redis客户端
redis = Redis(
    host="localhost",
    port=6379,
    db=0,
    password="your_password",
    decode_responses=True
)

# 初始化缓存管理器
cache = CacheManager(
    redis=redis,
    key_prefix="myapp:",
    default_expire=3600
)
```

### 2. 基本操作

```python
# 设置缓存
await cache.set("user:1", {"name": "张三", "age": 25}, expire=300)

# 获取缓存
user = await cache.get("user:1")

# 删除缓存
await cache.delete("user:1")

# 检查缓存是否存在
exists = await cache.exists("user:1")

# 设置过期时间
await cache.expire("user:1", timedelta(minutes=5))

# 获取剩余过期时间
ttl = await cache.ttl("user:1")
```

### 3. 计数器操作

```python
# 增加计数
count = await cache.incr("visits:page1")

# 减少计数
remain = await cache.decr("stock:item1")
```

### 4. 批量操作

```python
# 批量获取
users = await cache.mget(["user:1", "user:2", "user:3"])

# 批量设置
await cache.mset({
    "user:1": {"name": "张三"},
    "user:2": {"name": "李四"}
}, expire=300)

# 批量删除
await cache.delete_many(["user:1", "user:2"])

# 清除指定前缀的缓存
await cache.clear_prefix("user:")
```

### 5. 分布式锁

```python
# 获取锁
if await cache.acquire_lock("task:1", expire=10, timeout=5):
    try:
        # 执行任务
        pass
    finally:
        # 释放锁
        await cache.release_lock("task:1")
```

### 6. 缓存装饰器

```python
# 使用缓存装饰器
@cache.cache_decorator("user:{0}", expire=300)
async def get_user(user_id: int):
    # 从数据库获取用户信息
    return {"id": user_id, "name": "张三"}

# 调用函数时会自动使用缓存
user = await get_user(1)
```

## 高级特性

### 1. 自定义JSON编解码器

```python
from json import JSONEncoder, JSONDecoder

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

cache = CacheManager(
    redis=redis,
    json_encoder=CustomJSONEncoder(),
    json_decoder=JSONDecoder()
)
```

### 2. 自定义键生成策略

```python
def key_builder(*args, **kwargs):
    return f"custom:key:{args[0]}:{kwargs.get('type', 'default')}"

@cache.cache_decorator("", key_builder=key_builder)
async def get_data(id: int, type: str = "default"):
    return {"id": id, "type": type}
```

## 错误处理

缓存管理器会自动处理以下异常：

- 连接错误：返回默认值或操作失败标志
- JSON解析错误：返回默认值
- 类型错误：返回操作失败标志

## 性能优化建议

1. 合理设置过期时间
2. 使用批量操作代替单个操作
3. 避免存储过大的数据
4. 合理使用键前缀进行分类
5. 定期清理无用的缓存数据

## 测试

运行测试用例：

```bash
pytest backend/tests/core/cache/test_cache_manager.py -v
```

## 注意事项

1. 在生产环境中务必配置Redis密码
2. 合理设置锁的过期时间，避免死锁
3. 注意键的命名规范，建议使用冒号分隔
4. 缓存数据应该可以被重新生成
5. 建议对大型数据进行压缩存储 