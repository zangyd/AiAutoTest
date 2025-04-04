$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Jenkins安装脚本
param (
    [string]$ConfigPath = "jenkins-config.yaml",
    [string]$InstallDir = "E:\Jenkins"
)

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "需要管理员权限运行此脚本"
    exit 1
}

# 创建安装目录
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir
}

# 下载Jenkins
$jenkinsUrl = "https://get.jenkins.io/windows-stable/jenkins.msi"
$installerPath = Join-Path $InstallDir "jenkins.msi"
Write-Host "下载Jenkins安装包..."
Invoke-WebRequest -Uri $jenkinsUrl -OutFile $installerPath

# 安装Jenkins
Write-Host "安装Jenkins..."
Start-Process msiexec.exe -ArgumentList "/i `"$installerPath`" /qn" -Wait

# 配置Jenkins服务
Write-Host "配置Jenkins服务..."
$service = Get-Service -Name "Jenkins" -ErrorAction SilentlyContinue
if ($service) {
    # 停止服务
    Stop-Service -Name "Jenkins"
    
    # 设置服务启动类型为自动
    Set-Service -Name "Jenkins" -StartupType Automatic
    
    # 启动服务
    Start-Service -Name "Jenkins"
    Write-Host "Jenkins服务已启动"
} else {
    Write-Error "Jenkins服务未找到"
    exit 1
}

# 等待Jenkins启动
Write-Host "等待Jenkins启动..."
$maxAttempts = 30
$attempts = 0
$jenkinsUrl = "http://localhost:8090"

while ($attempts -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri $jenkinsUrl -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "Jenkins已成功启动"
            break
        }
    } catch {
        Start-Sleep -Seconds 10
        $attempts++
    }
}

if ($attempts -eq $maxAttempts) {
    Write-Error "Jenkins启动超时"
    exit 1
}

# 获取初始管理员密码
$adminPassword = Get-Content "E:\Jenkins\secrets\initialAdminPassword"
Write-Host "Jenkins初始管理员密码: $adminPassword"

Write-Host "Jenkins安装完成！"
Write-Host "请访问 http://localhost:8090 完成后续配置" 