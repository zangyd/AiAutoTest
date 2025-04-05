# GitHub Actions 工作流配置说明

## 目录
- [概述](#概述)
- [CI 工作流](#ci-工作流)
- [CD 工作流](#cd-工作流)
- [环境变量配置](#环境变量配置)
- [常见问题](#常见问题)

## 概述

本项目使用 GitHub Actions 实现自动化的持续集成（CI）和持续部署（CD）流程。工作流配置文件位于 `.github/workflows` 目录下：

- `code-check.yml`: 代码检查配置
- `ci.yml`: 持续集成配置
- `cd.yml`: 持续部署配置

## CI 工作流

### 触发条件
- 推送到 `main` 分支
- 创建 Pull Request 到 `main` 分支

### 工作流程
1. 代码检查（code-check）
   - 后端代码检查
     * Black：代码格式检查
     * isort：导入顺序检查
     * mypy：类型检查
     * flake8：代码风格检查
     * bandit：安全漏洞检查
     * safety：依赖安全检查
   - 前端代码检查
     * ESLint：代码规范检查
     * TypeScript：类型检查
     * Prettier：代码格式检查
     * npm audit：依赖安全检查

2. 后端测试（backend-test）
   - 启动测试环境
     * MySQL 8.0
     * MongoDB 6.0
     * Redis 6.2
   - 运行 Python 测试
     * 安装依赖
     * 执行单元测试

3. 前端测试（frontend-test）
   - 安装 Node.js 环境
   - 安装项目依赖
   - 运行单元测试
   - 构建项目

### 测试环境配置
```yaml
# MySQL
- 端口: 3306
- 用户名: root
- 密码: Autotest@2024
- 数据库: autotest

# MongoDB
- 端口: 27017
- 用户名: admin
- 密码: Autotest@2024

# Redis
- 端口: 6379
- 密码: Autotest@2024
```

## CD 工作流

### 触发条件
- 推送到 `main` 分支
- 创建版本标签（格式：`v*`）

### 工作流程
1. 构建和推送 Docker 镜像
   - 构建后端镜像
   - 构建前端镜像
   - 推送到 Docker Hub

2. 服务器部署
   - 通过 SSH 连接服务器
   - 拉取最新镜像
   - 使用 docker-compose 启动服务

### 镜像标签规则
- 最新版本：`latest`
- 版本发布：`v1.0.0`（遵循语义化版本）

## 环境变量配置

### 必需的 Secrets
在 GitHub 仓库的 Settings -> Secrets and variables -> Actions 中配置以下密钥：

1. Docker Hub 配置
   - `DOCKERHUB_USERNAME`: Docker Hub 用户名
   - `DOCKERHUB_TOKEN`: Docker Hub 访问令牌

2. 部署服务器配置
   - `SERVER_HOST`: 服务器地址
   - `SERVER_USERNAME`: 服务器用户名
   - `SERVER_SSH_KEY`: 服务器 SSH 私钥

### 配置步骤
1. 生成 Docker Hub 访问令牌
   - 访问 Docker Hub -> Account Settings -> Security
   - 创建新的访问令牌
   - 复制令牌值

2. 配置服务器 SSH 访问
   ```bash
   # 生成 SSH 密钥对
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   
   # 将公钥添加到服务器
   ssh-copy-id -i ~/.ssh/id_rsa.pub username@server_host
   
   # 复制私钥内容
   cat ~/.ssh/id_rsa
   ```

3. 添加 GitHub Secrets
   - 访问仓库 Settings
   - 选择 Secrets and variables -> Actions
   - 点击 "New repository secret"
   - 添加所有必需的密钥

## 常见问题

### 1. 代码检查失败
- 格式问题
  * 运行 `black .` 自动格式化Python代码
  * 运行 `isort .` 自动排序导入
  * 运行 `npm run format` 格式化前端代码
- 类型问题
  * 检查Python类型注解是否正确
  * 检查TypeScript类型定义是否完整
- 安全问题
  * 更新有安全隐患的依赖包
  * 检查并修复代码中的安全隐患

### 2. Docker 构建失败
- 检查 Dockerfile 是否存在
- 验证构建上下文路径
- 确认 Docker Hub 凭证正确

### 3. 部署失败
- 验证服务器 SSH 连接
- 检查服务器目录权限
- 确认 docker-compose.yml 存在

### 4. 测试环境问题
- 检查数据库连接配置
- 验证环境变量设置
- 确认依赖安装正确

### 5. 版本发布流程
1. 创建新的版本标签
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. 监控部署状态
   - 查看 Actions 页面的工作流运行状态
   - 检查服务器日志
   - 验证服务是否正常运行 