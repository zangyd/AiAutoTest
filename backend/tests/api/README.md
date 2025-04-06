# API 测试指南

## 目录结构

```
api/
├── config/             # 配置文件目录
│   ├── __init__.py
│   └── test_config.py # 测试配置文件
├── utils/             # 工具类目录
│   ├── __init__.py
│   └── test_client.py # HTTP客户端工具
├── fixtures/          # 测试固件目录
├── test_cases/        # 测试用例目录
└── __init__.py
```

## 快速开始

### 1. 环境配置

在项目根目录下创建 `.env` 文件（如果不存在），添加以下配置：

```bash
# API测试配置
TEST_API_HOST=localhost        # API服务器地址
TEST_API_PORT=8000            # API服务器端口
TEST_API_PROTOCOL=http        # 协议(http/https)
TEST_API_VERSION=v1           # API版本

# 测试账号配置
TEST_USERNAME=test_user       # 测试用户名
TEST_PASSWORD=test_password   # 测试密码

# 超时配置
TEST_REQUEST_TIMEOUT=10       # 请求超时时间(秒)
```

### 2. 编写测试用例

在 `test_cases` 目录下创建测试文件，例如 `test_auth.py`：

```python
import pytest
from ..utils.test_client import TestClient

@pytest.fixture
def client():
    """创建测试客户端"""
    with TestClient() as client:
        yield client

def test_login_success(client):
    """测试登录成功"""
    response = client.post("/auth/login", json={
        "username": "test_user",
        "password": "test_password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 3. 运行测试

```bash
# 运行所有API测试
pytest backend/tests/api/test_cases/

# 运行特定测试文件
pytest backend/tests/api/test_cases/test_auth.py

# 运行特定测试用例
pytest backend/tests/api/test_cases/test_auth.py::test_login_success
```

## 测试工具使用说明

### TestClient 使用方法

TestClient 提供了常用的 HTTP 方法封装：

```python
from api.utils.test_client import TestClient

# 使用上下文管理器
with TestClient() as client:
    # GET 请求
    response = client.get("/users")
    
    # POST 请求
    response = client.post("/users", json={
        "username": "new_user",
        "email": "user@example.com"
    })
    
    # PUT 请求
    response = client.put("/users/1", json={
        "email": "updated@example.com"
    })
    
    # DELETE 请求
    response = client.delete("/users/1")
```

### 登录认证

TestClient 提供了登录方法来获取认证令牌：

```python
async def test_authenticated_request(client):
    # 登录获取token
    await client.login()
    
    # 发送带认证的请求
    response = client.get("/protected-resource")
    assert response.status_code == 200
```

## 测试配置说明

`test_config.py` 提供了以下配置项：

- `TEST_API_HOST`: API服务器地址
- `TEST_API_PORT`: API服务器端口
- `TEST_API_PROTOCOL`: 协议(http/https)
- `TEST_API_VERSION`: API版本
- `TEST_USERNAME`: 测试用户名
- `TEST_PASSWORD`: 测试密码
- `TEST_REQUEST_TIMEOUT`: 请求超时时间

可以通过 `test_settings` 访问这些配置：

```python
from api.config.test_config import test_settings

print(test_settings.api_base_url)  # 完整的API基础URL
```

## 最佳实践

1. **测试用例组织**
   - 按功能模块组织测试文件
   - 使用清晰的命名约定
   - 每个测试文件专注于一个功能模块

2. **固件使用**
   - 将通用的测试数据和设置放在 fixtures 目录
   - 使用 pytest fixtures 进行资源管理
   - 避免测试间的状态依赖

3. **异常处理**
   - 测试异常情况和边界条件
   - 使用适当的断言验证结果
   - 清理测试产生的数据

4. **测试隔离**
   - 每个测试用例应该是独立的
   - 避免测试间的相互依赖
   - 使用临时数据而不是共享数据

## 常见问题

1. **测试无法连接到API服务器**
   - 检查环境变量配置
   - 确认API服务是否正在运行
   - 验证网络连接和防火墙设置

2. **认证失败**
   - 检查测试用户凭据
   - 确认token是否正确设置
   - 验证认证服务是否正常

3. **测试超时**
   - 调整 `TEST_REQUEST_TIMEOUT` 设置
   - 检查网络延迟
   - 优化测试执行效率

## 贡献指南

1. 遵循项目的编码规范
2. 为新功能编写测试用例
3. 更新文档以反映变更
4. 提交前进行本地测试

## 更新日志

- 2024-04-05: 初始版本
  - 创建基础目录结构
  - 实现TestClient
  - 添加基础配置 