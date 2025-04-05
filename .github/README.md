# 自动化测试平台 GitHub 工作流说明

## 目录
- [工作流概述](#工作流概述)
- [工作流配置](#工作流配置)
- [环境配置](#环境配置)
- [使用指南](#使用指南)
- [常见问题](#常见问题)

## 工作流概述

本项目采用完整的 CI/CD 工作流体系，包含以下主要工作流：

### 1. 代码检查工作流 (code-check.yml)
- 代码风格检查
- 类型检查
- 安全漏洞扫描
- 依赖审查

### 2. 持续集成工作流 (ci.yml)
- 单元测试
- 集成测试
- 端到端测试
- 测试覆盖率报告

### 3. 构建工作流 (build.yml)
- Docker镜像构建
- 制品打包
- 版本管理

### 4. 发布工作流 (release.yml)
- 版本发布
- 变更日志生成
- 制品发布

### 5. 部署工作流 (cd.yml)
- 环境部署
- 服务启动
- 健康检查
- 回滚机制

### 6. 流水线工作流 (pipeline.yml)
- 完整CI/CD流程
- 多环境支持
- 自动化测试
- 质量门禁

## 工作流配置

### 触发条件

1. **代码检查工作流**
   - Push到任意分支
   - Pull Request到main或develop分支
   - 每日定时运行

2. **持续集成工作流**
   - Push到main或develop分支
   - Pull Request到main或develop分支
   - 手动触发

3. **构建工作流**
   - Push到main或develop分支
   - 版本标签创建
   - 手动触发

4. **发布工作流**
   - 创建Release标签
   - 手动触发

5. **部署工作流**
   - Release发布
   - 手动触发

6. **流水线工作流**
   - Push到main或develop分支
   - Pull Request到main或develop分支
   - 每日凌晨2点自动运行
   - 手动触发

### 工作流矩阵

```yaml
测试矩阵:
  test-type: [unit, integration, e2e]
  python-version: ['3.10']
  node-version: ['18']
  os: [ubuntu-latest]

环境矩阵:
  environment: [dev, test, staging, prod]
  database: [MySQL 8.0, MongoDB 6.0, Redis 6.2]
```

## 环境配置

### 必需的Secrets配置

1. **认证凭据**
```yaml
DOCKERHUB_USERNAME: Docker Hub用户名
DOCKERHUB_TOKEN: Docker Hub访问令牌
GITHUB_TOKEN: GitHub访问令牌
```

2. **服务器配置**
```yaml
SERVER_HOST: 服务器地址
SERVER_USERNAME: 服务器用户名
SERVER_SSH_KEY: SSH私钥
```

3. **数据库配置**
```yaml
DB_PASSWORD: MySQL密码
MONGODB_USER: MongoDB用户名
MONGODB_PASSWORD: MongoDB密码
REDIS_PASSWORD: Redis密码
```

4. **通知配置**
```yaml
SLACK_WEBHOOK: Slack通知地址
```

### 环境变量配置

```yaml
PYTHON_VERSION: '3.10'
NODE_VERSION: '18'
MYSQL_DATABASE: 'autotest'
CACHE_KEY_PREFIX: 'v1'
```

## 使用指南

### 1. 开发工作流

1. 创建功能分支
```bash
git checkout -b feature/xxx
```

2. 提交代码
```bash
git add .
git commit -m "feat: xxx"
git push origin feature/xxx
```

3. 创建Pull Request
- 目标分支选择develop
- 填写PR描述
- 等待CI检查通过
- 请求代码审查

### 2. 发布工作流

1. 创建Release分支
```bash
git checkout -b release/v1.0.0
```

2. 更新版本号
```bash
# 修改version文件
echo "1.0.0" > VERSION
git add VERSION
git commit -m "chore: bump version to 1.0.0"
```

3. 创建Release标签
```bash
git tag v1.0.0
git push origin v1.0.0
```

### 3. 部署工作流

1. 手动触发部署
- 访问Actions页面
- 选择CD工作流
- 点击"Run workflow"
- 选择目标环境

2. 监控部署状态
- 查看部署日志
- 检查服务状态
- 验证功能正常

### 4. 回滚流程

1. 触发回滚
```bash
# 回退到指定版本
git tag v1.0.0-rollback
git push origin v1.0.0-rollback
```

2. 确认回滚
- 检查回滚结果
- 验证服务状态
- 通知相关人员

## 常见问题

### 1. 代码检查失败

**问题**: 代码风格检查不通过
**解决方案**:
```bash
# 后端代码格式化
black backend/
isort backend/

# 前端代码格式化
cd frontend
npm run format
```

### 2. 测试失败

**问题**: 测试环境服务未启动
**解决方案**:
- 检查数据库配置
- 验证环境变量
- 确认服务健康状态

### 3. 构建失败

**问题**: Docker构建超时
**解决方案**:
- 优化Dockerfile
- 使用构建缓存
- 增加构建超时时间

### 4. 部署失败

**问题**: SSH连接失败
**解决方案**:
- 验证SSH密钥配置
- 检查服务器防火墙
- 确认网络连接

### 5. 版本发布问题

**问题**: 制品发布失败
**解决方案**:
- 检查版本号格式
- 验证发布权限
- 确认制品完整性 