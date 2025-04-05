# Git提交信息规范

## 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

## Type类型
- feat: 新功能
- fix: Bug修复
- docs: 文档更新
- style: 代码格式（不影响代码运行的变动）
- refactor: 重构（既不是新增功能，也不是修改bug的代码变动）
- test: 增加测试
- chore: 构建过程或辅助工具的变动

## Scope范围
- 用于说明 commit 影响的范围
- 例如：backend, frontend, database, auth等

## Subject主题
- 简短描述，不超过50个字符
- 以动词开头，使用第一人称现在时
- 第一个字母小写
- 结尾不加句号

## Body正文
- 对本次提交的详细描述
- 可以分多行
- 说明代码变动的动机，以及与以前行为的对比

## Footer脚注
- 不兼容变动：以BREAKING CHANGE开头
- 关闭Issue：Closes #123, Fixes #123

## 示例
```
feat(auth): add user authentication

- Add JWT token generation
- Implement login endpoint
- Add password hashing

Closes #123
```

## 注意事项
1. 每次提交应该是完整的功能或修复
2. 提交信息要清晰明了
3. 避免无意义的提交信息
4. 遵循团队统一的规范 