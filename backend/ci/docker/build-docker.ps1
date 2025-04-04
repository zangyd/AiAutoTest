$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Docker构建脚本
param(
    [string]$Environment = "development",
    [switch]$ForceBuild,
    [switch]$NoPull
)

# 设置错误操作
$ErrorActionPreference = "Stop"

# 检查环境参数
$validEnvironments = @("development", "testing", "production")
if ($validEnvironments -notcontains $Environment) {
    Write-Error "无效的环境参数。请使用: $($validEnvironments -join ', ')"
    exit 1
}

# 检查Docker环境
Write-Host "检查Docker环境..." -ForegroundColor Cyan
$checkScript = Join-Path $PSScriptRoot "check-docker-env.ps1"
if (Test-Path $checkScript) {
    & $checkScript
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker环境检查失败，请先解决环境问题"
        exit 1
    }
}
else {
    Write-Warning "未找到环境检查脚本，跳过环境检查"
}

# 设置构建参数
$buildArgs = @(
    "--build-arg", "ENV=$Environment"
)

if ($ForceBuild) {
    $buildArgs += "--no-cache"
}

# 拉取最新镜像
if (-not $NoPull) {
    Write-Host "拉取最新基础镜像..." -ForegroundColor Cyan
    docker-compose pull
}

# 构建Docker镜像
try {
    Write-Host "开始构建Docker镜像..." -ForegroundColor Cyan
    $composeFile = Join-Path $PSScriptRoot "docker-compose.yml"
    
    if (-not (Test-Path $composeFile)) {
        Write-Error "未找到docker-compose.yml文件"
        exit 1
    }

    # 构建镜像
    $buildCommand = "docker-compose -f $composeFile build $buildArgs"
    Write-Host "执行构建命令: $buildCommand" -ForegroundColor Yellow
    Invoke-Expression $buildCommand

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker镜像构建失败"
        exit 1
    }

    Write-Host "Docker镜像构建成功！" -ForegroundColor Green

    # 显示构建的镜像
    Write-Host "`n构建的镜像列表：" -ForegroundColor Cyan
    docker images | Select-Object -First 5

}
catch {
    Write-Error "构建过程中发生错误: $_"
    exit 1
}

# 提示下一步操作
Write-Host "`n要启动服务，请运行：" -ForegroundColor Yellow
Write-Host "docker-compose -f $composeFile up -d" -ForegroundColor Gray 