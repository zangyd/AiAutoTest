$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Docker环境检查脚本
Write-Host "开始检查Docker环境..." -ForegroundColor Cyan

# 检查Docker是否安装
$dockerInstalled = $false
try {
    $dockerVersion = docker --version
    Write-Host "Docker已安装: $dockerVersion" -ForegroundColor Green
    $dockerInstalled = $true
}
catch {
    Write-Host "Docker未安装或未正确配置" -ForegroundColor Red
}

# 检查Docker Compose是否安装
$composeInstalled = $false
try {
    $composeVersion = docker-compose --version
    Write-Host "Docker Compose已安装: $composeVersion" -ForegroundColor Green
    $composeInstalled = $true
}
catch {
    Write-Host "Docker Compose未安装或未正确配置" -ForegroundColor Red
}

# 检查Docker服务状态
$serviceRunning = $false
try {
    $service = Get-Service -Name "docker" -ErrorAction Stop
    if ($service.Status -eq "Running") {
        Write-Host "Docker服务正在运行" -ForegroundColor Green
        $serviceRunning = $true
    }
    else {
        Write-Host "Docker服务未运行" -ForegroundColor Red
    }
}
catch {
    Write-Host "无法获取Docker服务状态" -ForegroundColor Red
}

# 检查必要的Docker镜像
$allImagesPresent = $true
$requiredImages = @("python:3.10-slim", "mongo:latest", "redis:latest", "mysql:8.0")
foreach ($image in $requiredImages) {
    try {
        $imageExists = docker images -q $image
        if ($imageExists) {
            Write-Host "镜像 $image 已存在" -ForegroundColor Green
        } else {
            Write-Host "镜像 $image 不存在，需要拉取" -ForegroundColor Yellow
            $allImagesPresent = $false
        }
    } catch {
        Write-Host "检查Docker镜像时发生错误" -ForegroundColor Red
        $allImagesPresent = $false
    }
}

# 检查Docker网络
$networkOk = $false
try {
    $networkName = "app-network"
    $networkExists = docker network ls --filter name=$networkName -q
    if ($networkExists) {
        Write-Host "Docker网络 $networkName 已存在" -ForegroundColor Green
        $networkOk = $true
    } else {
        Write-Host "Docker网络 $networkName 不存在，需要创建" -ForegroundColor Yellow
    }
} catch {
    Write-Host "检查Docker网络时发生错误" -ForegroundColor Red
}

# 输出最终结果
$checksPassed = $dockerInstalled -and $composeInstalled -and $serviceRunning -and $allImagesPresent -and $networkOk

if ($checksPassed) {
    Write-Host "`nDocker环境检查通过！" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nDocker环境检查失败，请解决上述问题。" -ForegroundColor Red
    exit 1
}