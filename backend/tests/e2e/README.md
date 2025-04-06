# E2E测试目录结构说明

## 目录结构

```
e2e/
├── config/                 # 配置文件
│   └── browser/           # 浏览器相关配置
│       └── playwright_config.py
├── data/                  # 测试数据
│   ├── test_data/        # 测试输入数据
│   └── test_results/     # 测试结果数据
├── fixtures/              # 测试固件
├── pages/                 # 页面对象
│   └── common/           # 通用页面组件
│       └── base_page.py
├── tests/                 # 测试用例
│   ├── auth/             # 认证相关测试
│   ├── dashboard/        # 仪表盘相关测试
│   └── common/           # 通用功能测试
├── utils/                 # 工具类
│   ├── decorators/       # 装饰器
│   ├── drivers/          # 驱动管理
│   └── helpers/          # 辅助工具
└── conftest.py           # 全局测试配置

```

## 主要组件说明

1. **配置文件 (config/)**
   - `playwright_config.py`: Playwright浏览器配置

2. **页面对象 (pages/)**
   - `base_page.py`: 基础页面类，提供通用页面操作方法

3. **工具类 (utils/)**
   - `browser_driver.py`: 浏览器驱动管理
   - `test_decorators.py`: 测试装饰器（日志、重试等）
   - `test_helper.py`: 测试辅助工具

4. **测试用例 (tests/)**
   - `auth/`: 认证相关测试（登录、注册等）
   - `dashboard/`: 仪表盘功能测试
   - `common/`: 通用功能测试

## 使用方法

1. **运行所有测试**
   ```bash
   pytest tests/
   ```

2. **运行特定模块测试**
   ```bash
   pytest tests/auth/test_login.py
   ```

3. **运行特定测试用例**
   ```bash
   pytest tests/auth/test_login.py::test_login_success
   ```

4. **使用标记运行测试**
   ```bash
   pytest -m "not skip"  # 运行未跳过的测试
   ```

## 开发规范

1. 测试文件命名：`test_*.py`
2. 测试类命名：`Test*`
3. 测试方法命名：`test_*`
4. 使用页面对象模式
5. 合理使用测试装饰器
6. 保持测试数据独立
7. 编写清晰的测试文档

## 注意事项

1. 运行测试前确保目标服务已启动
2. 使用 `conftest.py` 管理共享的fixture
3. 使用 `test_helper.py` 处理测试数据
4. 合理使用重试机制处理不稳定的测试
5. 及时清理测试数据和结果 