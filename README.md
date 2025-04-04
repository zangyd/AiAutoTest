# 自动化测试平台

## 项目简介
基于Python FastAPI和Vue3的现代化自动化测试平台，集成了AI驱动的测试用例生成、自动化测试执行、视觉测试和智能报告分析等功能。

## 技术栈
### 前端
- Vue 3
- TypeScript
- Element Plus
- Pinia
- Vue Router

### 后端
- Python 3.10+
- FastAPI
- SQLAlchemy
- MongoDB
- Redis
- LangChain
- OpenCV

### 测试框架
- Pytest
- Playwright
- Appium

## 开发环境要求
- Node.js 16+
- Python 3.10+
- MySQL 8.0+
- MongoDB 5.0+
- Redis 6.0+

## 快速开始

### 后端服务
1. 安装Python依赖
```bash
cd backend
pip install -r requirements/base.txt
```

2. 启动后端服务
```bash
cd backend/src
uvicorn main:app --reload
```

### 前端服务
1. 安装Node.js依赖
```bash
cd frontend
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

## 项目结构
```
/
├── frontend/          # 前端项目
├── backend/          # 后端项目
├── docs/             # 项目文档
├── scripts/          # 项目脚本
└── tests/           # 测试文件
```

## 文档
详细文档请参考 `docs` 目录：
- API文档
- 设计文档
- 使用指南

## 贡献指南
请参考 `CONTRIBUTING.md` 文件了解如何参与项目开发。

## 许可证
本项目采用 MIT 许可证
