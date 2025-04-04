# 自动化部署脚本
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("development", "testing", "production")]
    [string]$Environment,
    
    [switch]$SkipBuild,
    [switch]$SkipTests,
    [switch]$Force
)

# 设置错误操作
$ErrorActionPreference = "Stop"

# 定义颜色函数
function Write-Step {
    param([string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "错误: $Message" -ForegroundColor Red
}

# 检查必要工具
Write-Step "检查必要工具"
$tools = @("git", "docker", "docker-compose")
foreach ($tool in $tools) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Error "未找到 $tool，请确保已安装并添加到PATH中"
        exit 1
    }
}
Write-Success "所有必要工具检查通过"

# 获取当前Git分支
$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Step "当前Git分支: $currentBranch"

# 环境检查
if ($Environment -eq "production" -and $currentBranch -ne "main") {
    if (-not $Force) {
        Write-Error "生产环境部署必须从main分支进行"
        exit 1
    }
    Write-Warning "强制从非main分支部署到生产环境"
}

# 拉取最新代码
Write-Step "拉取最新代码"
git pull
if ($LASTEXITCODE -ne 0) {
    Write-Error "拉取代码失败"
    exit 1
}

# 运行测试
if (-not $SkipTests) {
    Write-Step "运行测试"
    # 后端测试
    & pytest backend/tests
    if ($LASTEXITCODE -ne 0) {
        Write-Error "后端测试失败"
        exit 1
    }
    
    # 前端测试
    & npm test
    if ($LASTEXITCODE -ne 0) {
        Write-Error "前端测试失败"
        exit 1
    }
    Write-Success "所有测试通过"
}

# 构建Docker镜像
if (-not $SkipBuild) {
    Write-Step "构建Docker镜像"
    $buildScript = Join-Path $PSScriptRoot "docker/build-docker.ps1"
    & $buildScript -Environment $Environment
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker构建失败"
        exit 1
    }
    Write-Success "Docker构建完成"
}

# 停止现有服务
Write-Step "停止现有服务"
$composeFile = Join-Path $PSScriptRoot "docker/docker-compose.yml"
docker-compose -f $composeFile down
Write-Success "现有服务已停止"

# 启动新服务
Write-Step "启动新服务"
$env:COMPOSE_PROJECT_NAME = "autotest-$Environment"
docker-compose -f $composeFile up -d
if ($LASTEXITCODE -ne 0) {
    Write-Error "服务启动失败"
    exit 1
}

# 检查服务健康状态
Write-Step "检查服务健康状态"
$services = docker-compose -f $composeFile ps --services
foreach ($service in $services) {
    $status = docker-compose -f $composeFile ps $service
    if ($status -match "Up") {
        Write-Success "$service 服务运行正常"
    }
    else {
        Write-Error "$service 服务可能存在问题"
        Write-Host "服务日志:"
        docker-compose -f $composeFile logs $service --tail 50
        exit 1
    }
}

# 部署完成
Write-Success "`n部署完成！环境: $Environment"
Write-Host "`n访问地址:"
Write-Host "后端API: http://localhost:8000"
Write-Host "前端页面: http://localhost:8080"

# 显示服务状态
Write-Host "`n服务状态:"
docker-compose -f $composeFile ps 