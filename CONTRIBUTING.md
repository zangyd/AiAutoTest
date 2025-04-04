# 贡献指南

## 开发流程

### 1. 分支管理
- `main`: 主分支，用于发布
- `develop`: 开发分支，所有功能开发都基于此分支
- `feature/*`: 功能分支，用于开发新功能
- `bugfix/*`: 修复分支，用于修复问题
- `release/*`: 发布分支，用于版本发布

### 2. 提交规范
提交信息格式：
```
<type>(<scope>): <subject>

<body>

<footer>
```

类型（type）：
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建过程或辅助工具的变动

### 3. 开发规范
- 遵循项目既定的代码规范
- 保持代码简洁清晰
- 编写必要的注释
- 确保测试覆盖

### 4. 提交PR流程
1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 编写测试
5. 提交PR
6. 等待代码审查
7. 合并代码

### 5. 测试要求
- 单元测试覆盖率 > 80%
- 集成测试覆盖主要功能
- 确保所有测试通过

### 6. 文档要求
- 更新相关文档
- 添加必要的注释
- 编写使用说明

### 7. 版本发布
- 遵循语义化版本
- 更新版本日志
- 标记版本标签

## 开发环境搭建

### 1. 前端开发环境
```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev
```

### 2. 后端开发环境
```bash
# 创建虚拟环境
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements/dev.txt

# 启动服务
cd src
uvicorn main:app --reload
```

## 问题反馈
- 使用 GitHub Issues 提交问题
- 提供详细的问题描述
- 附上必要的日志和截图

## 联系方式
- 项目讨论：GitHub Discussions
- 技术支持：GitHub Issues
- 安全问题：请直接联系项目维护者 