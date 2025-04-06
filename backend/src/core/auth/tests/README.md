# 认证模块测试指南

## 目录结构

```
core/auth/
├── fixtures/           # 测试固件
│   ├── __init__.py
│   ├── users.py       # 用户数据固件
│   └── tokens.py      # Token相关固件
├── test_cases/        # 测试用例
│   ├── __init__.py
│   ├── test_jwt.py    # JWT相关测试
│   ├── test_login.py  # 登录相关测试
│   └── test_users.py  # 用户管理测试
└── __init__.py
```

## 测试范围

### 1. JWT认证测试
- Token生成与验证
- Token过期处理
- Token刷新机制
- Token黑名单
- 无效Token处理

### 2. 登录认证测试
- 用户名密码登录
- 邮箱登录
- 图形验证码验证
- 登录失败处理
- 账号锁定机制
- 密码重试限制

### 3. 用户管理测试
- 用户信息管理
- 密码管理
- 权限验证
- 会话管理
- 安全策略

## 测试用例编写规范

### 1. 命名规范

```python
def test_should_success_when_valid_credentials():
    """测试使用有效凭据时登录成功"""
    pass

def test_should_fail_when_invalid_password():
    """测试使用无效密码时登录失败"""
    pass

def test_should_lock_account_after_max_attempts():
    """测试超过最大重试次数后账号锁定"""
    pass
```

### 2. 固件使用

```python
import pytest
from .fixtures.users import create_test_user
from .fixtures.tokens import generate_test_token

@pytest.fixture
def test_user():
    """创建测试用户固件"""
    user = create_test_user()
    yield user
    # 清理测试数据
    user.delete()

@pytest.fixture
def valid_token(test_user):
    """创建有效token固件"""
    return generate_test_token(test_user)
```

### 3. 测试用例示例

```python
async def test_login_success(test_client, test_user):
    """测试登录成功场景"""
    response = await test_client.post("/auth/login", json={
        "username": test_user.username,
        "password": "test_password"
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

async def test_token_refresh(test_client, valid_token):
    """测试token刷新"""
    response = await test_client.post("/auth/refresh", headers={
        "Authorization": f"Bearer {valid_token}"
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## 测试数据管理

### 1. 测试用户配置

在 `.env.test` 文件中配置测试用户信息：

```bash
# 测试用户配置
TEST_ADMIN_USERNAME=admin
TEST_ADMIN_PASSWORD=admin_password
TEST_USER_USERNAME=test_user
TEST_USER_PASSWORD=test_password

# JWT配置
TEST_JWT_SECRET=test_secret
TEST_JWT_ALGORITHM=HS256
TEST_ACCESS_TOKEN_EXPIRE_MINUTES=30
TEST_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 2. 数据库固件

```python
@pytest.fixture(scope="session")
def test_db():
    """测试数据库固件"""
    # 创建测试数据库
    db = create_test_database()
    
    # 运行迁移
    run_migrations()
    
    yield db
    
    # 清理测试数据库
    drop_test_database()
```

## 运行测试

### 1. 运行所有认证测试

```bash
pytest backend/tests/core/auth/test_cases/
```

### 2. 运行特定测试类型

```bash
# 运行JWT相关测试
pytest backend/tests/core/auth/test_cases/test_jwt.py

# 运行登录相关测试
pytest backend/tests/core/auth/test_cases/test_login.py

# 运行用户管理测试
pytest backend/tests/core/auth/test_cases/test_users.py
```

### 3. 运行带标记的测试

```bash
# 运行所有安全相关测试
pytest -m security backend/tests/core/auth/

# 运行所有集成测试
pytest -m integration backend/tests/core/auth/
```

## 测试覆盖率要求

1. **代码覆盖率**
   - 行覆盖率 > 90%
   - 分支覆盖率 > 85%
   - 路径覆盖率 > 80%

2. **场景覆盖**
   - 正常流程测试
   - 异常流程测试
   - 边界条件测试
   - 安全漏洞测试

## 调试指南

### 1. 开启详细日志

```bash
pytest -v --log-cli-level=DEBUG backend/tests/core/auth/
```

### 2. 使用调试模式

```bash
pytest --pdb backend/tests/core/auth/test_cases/test_login.py
```

### 3. 查看测试覆盖率报告

```bash
pytest --cov=backend.core.auth backend/tests/core/auth/
```

## 常见问题

1. **测试数据清理**
   - 使用 `pytest.fixture` 的清理机制
   - 在测试完成后清理测试数据
   - 避免测试数据污染

2. **异步测试处理**
   - 使用 `pytest-asyncio` 处理异步测试
   - 正确使用 `async/await` 语法
   - 处理异步超时情况

3. **环境隔离**
   - 使用独立的测试数据库
   - 避免修改生产配置
   - 保持测试环境隔离

## 更新日志

- 2024-04-05: 初始版本
  - 创建认证测试基础结构
  - 添加JWT测试用例
  - 实现登录测试用例
  - 添加用户管理测试 