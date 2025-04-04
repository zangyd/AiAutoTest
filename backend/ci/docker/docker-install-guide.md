# Docker Desktop 安装指南

## 系统要求
- Windows 10 64位：专业版、企业版或教育版（内部版本 19041 或更高版本）
- 启用 WSL 2 功能
- 64位处理器，支持SLAT
- 至少4GB系统内存

## 安装步骤

1. 下载 Docker Desktop
   - 访问 [Docker Desktop官网](https://www.docker.com/products/docker-desktop)
   - 点击"Download for Windows"下载安装程序

2. 安装 WSL 2
   ```powershell
   # 以管理员身份运行PowerShell，执行以下命令：
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```
   - 重启电脑
   - 下载并安装 [WSL2 Linux内核更新包](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi)
   - 设置WSL 2为默认版本：
   ```powershell
   wsl --set-default-version 2
   ```

3. 安装 Docker Desktop
   - 运行下载的Docker Desktop Installer.exe
   - 按照安装向导完成安装
   - 安装完成后重启电脑

4. 验证安装
   - 打开PowerShell，运行以下命令：
   ```powershell
   docker --version
   docker-compose --version
   ```

5. 配置Docker Desktop
   - 启动Docker Desktop
   - 在系统托盘中右键Docker图标
   - 选择"Settings"
   - 在"Resources" > "WSL Integration"中启用需要的Linux发行版

## 常见问题

1. WSL 2安装失败
   - 确保Windows版本满足要求
   - 在BIOS中启用虚拟化
   - 完整重启电脑

2. Docker Desktop启动失败
   - 检查WSL 2是否正确安装
   - 检查虚拟化是否启用
   - 检查Windows功能中的"Hyper-V"和"Windows虚拟化平台"是否启用

3. 性能问题
   - 在Settings > Resources中调整内存限制
   - 在WSL 2配置文件中优化内存使用

## 下一步

安装完成后，运行以下脚本检查环境：
```powershell
.\check-docker-env.ps1
```

如果发现任何问题，请参考上述常见问题解决方案或联系技术支持。 