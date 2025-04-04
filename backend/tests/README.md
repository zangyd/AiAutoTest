# 自动化测试项目结构说明

## 目录结构

```
backend/tests/
├── browser/         # 浏览器自动化基础设施
│   ├── config/     # 浏览器配置
│   ├── utils/      # 浏览器工具
│   ├── tests/      # 测试用例
│   └── fixtures/   # 测试固件
├── e2e/            # Web端到端测试
│   ├── config/     # 端到端测试配置
│   ├── utils/      # 端到端测试工具
│   ├── tests/      # 测试用例
│   └── fixtures/   # 测试固件
├── mobile/         # 移动应用测试
│   ├── config/     # 移动测试配置
│   ├── utils/      # 移动测试工具
│   ├── tests/      # 测试用例
│   └── fixtures/   # 测试固件
├── api/            # 接口自动化测试
│   ├── config/     # 接口测试配置
│   ├── utils/      # 接口测试工具
│   ├── tests/      # 测试用例
│   └── fixtures/   # 测试固件
├── environments/   # 环境测试
│   ├── test_environment.py        # 基础环境测试
│   ├── test_opencv_environment.py # OpenCV环境测试
│   └── test_cicd_environment.py   # CI/CD环境测试
└── common/         # 共享组件
    ├── utils/      # 共享工具函数
    ├── fixtures/   # 共享测试固件
    └── config/     # 共享配置
```

## 各目录职责说明

### 1. browser 目录
- **用途**：提供基础的浏览器自动化能力
- **主要组件**：
  - `config/`：浏览器配置管理，支持Chrome、Firefox和Edge
  - `utils/`：浏览器操作工具类，封装Playwright常用操作
  - `tests/`：浏览器自动化测试用例
  - `fixtures/`：浏览器测试固件
- **特点**：
  - 作为基础设施供其他测试使用
  - 直接使用Playwright框架
  - 标准化的目录结构

### 2. e2e 目录
- **用途**：Web应用的端到端测试
- **主要组件**：
  - `config/`：端到端测试配置，包含Playwright配置
  - `utils/`：端到端测试工具函数
  - `tests/`：端到端测试用例
  - `fixtures/`：端到端测试固件
- **特点**：
  - 使用Page Object设计模式
  - 基于Playwright框架
  - 标准化的目录结构

### 3. mobile 目录
- **用途**：移动应用测试
- **主要组件**：
  - `config/`：Appium配置
  - `utils/`：移动测试工具
  - `tests/`：测试用例
  - `fixtures/`：测试固件
- **特点**：
  - 使用Appium框架
  - 采用Page Object设计模式
  - 包含设备管理和配置

### 4. api 目录
- **用途**：提供接口自动化测试能力
- **主要组件**：
  - `config/`：接口测试配置，包含环境配置、请求配置等
  - `utils/`：接口测试工具，如请求封装、数据处理等
  - `tests/`：测试用例
  - `fixtures/`：测试固件，如数据准备、清理等
- **特点**：
  - 使用requests/httpx框架
  - 支持RESTful API测试
  - 包含接口性能测试
  - 支持接口数据验证

### 5. environments 目录
- **用途**：环境测试和验证
- **主要文件**：
  - `test_environment.py`：基础环境测试（Playwright、Appium、OpenCV）
  - `test_opencv_environment.py`：OpenCV环境专项测试
  - `test_cicd_environment.py`：CI/CD环境测试
- **特点**：
  - 验证测试环境依赖
  - 检查工具版本兼容性
  - 确保环境配置正确

### 6. common 目录
- **用途**：存放可在不同测试类型间共享的组件
- **主要组件**：
  - `utils/`：共享工具函数
  - `fixtures/`：共享测试固件
  - `config/`：共享配置
- **设计原则**：
  - 只放置真正需要共享的组件
  - 保持高内聚、低耦合
  - 避免重复代码

## 主要区别

1. **职责分离**：
   - `browser/`：提供基础的浏览器自动化能力
   - `e2e/`：专注于Web应用的端到端测试
   - `mobile/`：专注于移动应用测试
   - `api/`：专注于接口自动化测试
   - `environments/`：专注于环境测试和验证
   - `common/`：提供共享功能

2. **框架使用**：
   - `browser/`：直接使用Playwright
   - `e2e/`：使用Playwright + Page Object模式
   - `mobile/`：使用Appium + Page Object模式
   - `api/`：使用requests/httpx
   - `environments/`：使用pytest

3. **配置管理**：
   每个测试类型目录都包含四个标准子目录：
   - `config/`：特定类型的配置文件
   - `utils/`：特定类型的工具函数
   - `tests/`：测试用例
   - `fixtures/`：测试固件

## 维护建议

1. **目录结构**：
   - 保持统一的四层目录结构（config/utils/tests/fixtures）
   - 遵循各自框架的最佳实践
   - 避免在不同类型的测试目录间复制代码

2. **代码管理**：
   - 将可复用的代码移至common目录
   - 保持配置文件的独立性
   - 及时更新文档

3. **测试编写**：
   - 使用统一的测试结构和风格
   - 保持测试用例的独立性
   - 合理使用测试固件

4. **共享原则**：
   - 评估代码是否真正需要共享
   - 在common目录中维护清晰的文档
   - 定期审查和清理未使用的共享代码 