# 贡献指南

## 一、开发流程

### 1. 分支管理
- `main`: 主分支，用于发布
- `develop`: 开发分支，所有功能开发都基于此分支
- `feature/*`: 功能分支，用于开发新功能
- `bugfix/*`: 修复分支，用于修复问题
- `release/*`: 发布分支，用于版本发布
- `hotfix/*`: 紧急修复分支，用于生产环境紧急修复

### 2. 提交规范
提交信息格式：
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 2.1 类型（type）：
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式（不影响代码运行的变动）
- refactor: 重构（既不是新增功能，也不是修改bug的代码变动）
- test: 增加测试
- chore: 构建过程或辅助工具的变动
- perf: 性能优化
- ci: 持续集成相关
- revert: 回滚

#### 2.2 范围（scope）：
- 用于说明提交影响的范围
- 例如：auth, user, api, core等

#### 2.3 主题（subject）：
- 简短描述，不超过50个字符
- 以动词开头，使用第一人称现在时
- 第一个字母小写
- 结尾不加句号

#### 2.4 正文（body）：
- 详细描述改动内容
- 可以分多行
- 说明代码变动的动机

#### 2.5 页脚（footer）：
- 关闭Issue：Closes #123, Fixes #456
- 破坏性变动说明
- 关联提交：Related to #789

### 3. 开发规范

#### 3.1 代码风格
- Python代码遵循PEP 8规范
- 使用Black进行代码格式化
- 使用isort管理导入顺序
- JavaScript/TypeScript使用Prettier格式化
- 使用ESLint进行代码检查

#### 3.2 命名规范
- 类名：使用大驼峰命名法（PascalCase）
- 函数/方法：使用小驼峰命名法（camelCase）
- 变量：使用小驼峰命名法
- 常量：使用大写字母，下划线分隔
- 文件名：使用小写字母，连字符分隔

#### 3.3 注释规范
- 添加必要的文档字符串（docstring）
- 复杂逻辑需要添加详细注释
- 使用英文编写注释
- 保持注释的时效性

### 4. PR提交流程

#### 4.1 准备工作
1. Fork项目到个人仓库
2. 克隆个人仓库到本地
3. 添加上游仓库
4. 创建功能分支

#### 4.2 开发阶段
1. 编写代码
2. 添加测试
3. 运行测试确保通过
4. 更新文档
5. 提交代码

#### 4.3 提交PR
1. 推送代码到个人仓库
2. 创建Pull Request
3. 填写PR描述
4. 等待代码审查
5. 根据反馈修改
6. 合并代码

### 5. 测试要求

#### 5.1 测试覆盖
- 单元测试覆盖率不低于80%
- 核心功能必须有集成测试
- 新功能必须包含测试用例
- UI组件需要添加快照测试

#### 5.2 测试规范
- 测试代码放在tests目录下
- 测试文件命名：test_*.py
- 测试类命名：Test*
- 测试方法命名：test_*

### 6. 文档要求

#### 6.1 代码文档
- 添加详细的函数/方法文档
- 更新API文档
- 添加必要的代码注释
- 更新README.md

#### 6.2 变更文档
- 更新CHANGELOG.md
- 添加新功能使用说明
- 更新配置文档
- 更新部署文档

### 7. 版本发布

#### 7.1 版本号规范
- 主版本号：重大功能变更
- 次版本号：新功能发布
- 修订号：bug修复和小改动

#### 7.2 发布流程
1. 创建release分支
2. 更新版本号
3. 更新CHANGELOG
4. 创建版本标签
5. 合并到主分支
6. 发布版本

## 二、开发环境搭建

### 1. 前端开发环境
```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev

# 运行测试
npm run test

# 代码检查
npm run lint
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

# 运行测试
pytest

# 代码检查
black .
isort .
flake8
```

## 三、问题反馈

### 1. Issue提交
- 使用Issue模板
- 提供详细的问题描述
- 附上必要的日志和截图
- 说明复现步骤
- 标注问题类型和优先级

### 2. 安全问题
- 不要在Issue中提交安全漏洞
- 直接联系项目维护者
- 遵循安全漏洞披露政策

## 四、联系方式

### 1. 问题讨论
- GitHub Discussions：功能讨论和建议
- GitHub Issues：bug报告和任务跟踪

### 2. 技术支持
- 项目文档：docs/
- Wiki页面：项目Wiki
- 邮件支持：[项目邮箱]

### 3. 社区贡献
- 代码贡献：Pull Request
- 文档改进：docs/
- 问题反馈：Issues
- 功能建议：Discussions 