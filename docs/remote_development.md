# 远程开发指南

## 环境要求

- VSCode
- Python 3.10+
- Git

## 必需的VSCode插件

1. Remote - SSH
2. Python
3. Remote Development
4. GitLens (推荐)
5. Docker (推荐)

## 远程开发设置步骤

### 1. SSH配置

1. 在本地生成SSH密钥（如果没有）：
```bash
ssh-keygen -t rsa -b 4096
```

2. 配置SSH：
```bash
# ~/.ssh/config
Host autotest-server
    HostName your-server-ip
    User your-username
    Port 22
    IdentityFile ~/.ssh/id_rsa
    ForwardAgent yes
```

3. 将公钥添加到远程服务器：
```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub your-username@your-server-ip
```

### 2. VSCode连接

1. 打开VSCode
2. 按下 `F1` 或 `Ctrl+Shift+P`
3. 输入 `Remote-SSH: Connect to Host`
4. 选择 `autotest-server`

### 3. 项目设置

1. 打开项目文件夹：
   - File -> Open Folder -> /data/projects/autotest

2. 选择Python解释器：
   - `Ctrl+Shift+P` -> Python: Select Interpreter
   - 选择 `/data/projects/autotest/backend/venv/bin/python`

### 4. 开发工作流

1. 启动开发服务器：
   - 使用命令面板（`Ctrl+Shift+P`）
   - 运行任务：`Tasks: Run Task`
   - 选择 `Start Development Server`

2. 运行测试：
   - 使用命令面板
   - 运行任务：`Tasks: Run Task`
   - 选择 `Run Tests`

3. 代码格式化：
   - 使用命令面板
   - 运行任务：`Tasks: Run Task`
   - 选择 `Format Code`

4. 代码检查：
   - 使用命令面板
   - 运行任务：`Tasks: Run Task`
   - 选择 `Lint Code`

### 5. 调试

1. 启动调试会话：
   - 按下 `F5`
   - 选择调试配置：
     - `Python: FastAPI` - 启动并调试FastAPI服务器
     - `Python: Remote Attach` - 附加到运行中的进程
     - `Python: Current File` - 调试当前文件
     - `Python: Run Tests` - 调试测试

2. 调试功能：
   - 断点：点击行号左侧
   - 步进：F11
   - 步过：F10
   - 继续：F5
   - 查看变量：调试侧边栏

### 6. Git操作

所有Git操作都可以通过VSCode的源代码管理面板完成：
- 暂存更改
- 提交
- 推送/拉取
- 分支管理
- 查看历史

## 最佳实践

1. 代码质量
   - 保存时自动格式化
   - 定期运行lint检查
   - 编写测试用例

2. 调试技巧
   - 使用断点而不是print语句
   - 利用调试控制台执行代码
   - 使用watch表达式监控变量

3. 性能优化
   - 使用远程工作区而不是本地同步
   - 适当使用排除模式
   - 限制文件监视

4. 协作
   - 保持代码格式一致
   - 及时提交和推送更改
   - 使用有意义的提交消息

## 常见问题解决

1. SSH连接问题
   - 检查网络连接
   - 验证SSH密钥
   - 确认服务器防火墙设置

2. Python环境问题
   - 确保虚拟环境激活
   - 验证依赖安装
   - 检查PYTHONPATH设置

3. 调试问题
   - 确认debugpy已安装
   - 检查端口转发
   - 验证路径映射 