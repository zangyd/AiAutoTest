# 仓库目录结构规范

## 顶级目录结构
```
autotest/
├── backend/           # 后端代码目录
├── frontend/          # 前端代码目录
├── docs/             # 项目文档
├── tests/            # 测试代码
├── scripts/          # 工具脚本
├── .github/          # GitHub配置文件
├── .gitignore        # Git忽略文件
└── README.md         # 项目说明文档
```

## 后端目录结构
```
backend/
├── app/              # 应用代码
│   ├── api/         # API接口
│   ├── core/        # 核心功能
│   ├── models/      # 数据模型
│   └── utils/       # 工具函数
├── config/          # 配置文件
├── scripts/         # 管理脚本
└── tests/           # 测试代码
```

## 前端目录结构
```
frontend/
├── src/             # 源代码
│   ├── api/        # API请求
│   ├── assets/     # 静态资源
│   ├── components/ # 组件
│   ├── router/     # 路由配置
│   ├── store/      # 状态管理
│   └── views/      # 页面视图
├── public/         # 公共资源
└── tests/          # 测试代码
```

## 文档目录结构
```
docs/
├── api/            # API文档
├── architecture/   # 架构文档
├── database/       # 数据库文档
├── deployment/     # 部署文档
└── git/            # Git相关文档
```

## 测试目录结构
```
tests/
├── unit/           # 单元测试
├── integration/    # 集成测试
├── e2e/            # 端到端测试
└── performance/    # 性能测试
```

## 脚本目录结构
```
scripts/
├── setup/          # 环境搭建脚本
├── deploy/         # 部署脚本
├── backup/         # 备份脚本
└── maintenance/    # 维护脚本
```

## 命名规范
1. 目录名使用小写字母
2. 多个单词用连字符(-)分隔
3. 代码文件使用小写字母
4. 类文件使用大驼峰命名
5. 测试文件以test_开头

## 文件组织原则
1. 相关文件放在同一目录下
2. 保持目录结构清晰和统一
3. 避免目录层级过深
4. 遵循职责单一原则
5. 保持适度的模块化 