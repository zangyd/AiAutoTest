$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Jenkins插件安装脚本
param(
    [string]$JenkinsUrl = "http://localhost:8090",
    [string]$AdminUser = "admin",
    [string]$AdminPassword = "",
    [string]$PluginsFile = "plugins.txt"
)

# 检查参数
if (-not $AdminPassword) {
    Write-Error "请提供Jenkins管理员密码"
    exit 1
}

# 检查plugins.txt文件是否存在
if (-not (Test-Path $PluginsFile)) {
    Write-Error "插件配置文件 $PluginsFile 不存在"
    exit 1
}

# 创建临时目录
$TempDir = "temp_plugins"
if (-not (Test-Path $TempDir)) {
    New-Item -ItemType Directory -Path $TempDir | Out-Null
}

# 读取插件列表
$Plugins = Get-Content $PluginsFile | Where-Object { $_ -notmatch '^\s*#' -and $_ -notmatch '^\s*$' }

Write-Host "开始安装Jenkins插件..."

foreach ($Plugin in $Plugins) {
    $PluginName = $Plugin.Split(':')[0]
    Write-Host "正在安装插件: $PluginName"
    
    try {
        # 使用Jenkins CLI安装插件
        $InstallUrl = "$JenkinsUrl/pluginManager/install?plugin.$PluginName=true"
        $Headers = @{
            Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($AdminUser):$($AdminPassword)"))
        }
        
        Invoke-RestMethod -Uri $InstallUrl -Headers $Headers -Method Post
        Write-Host "插件 $PluginName 安装成功" -ForegroundColor Green
    }
    catch {
        Write-Error "安装插件 $PluginName 失败: $_"
    }
    
    # 等待一段时间确保插件安装完成
    Start-Sleep -Seconds 5
}

# 重启Jenkins以应用插件
Write-Host "正在重启Jenkins以应用插件更改..."
$RestartUrl = "$JenkinsUrl/restart"
try {
    Invoke-RestMethod -Uri $RestartUrl -Headers $Headers -Method Post
    Write-Host "Jenkins重启命令已发送" -ForegroundColor Green
}
catch {
    Write-Error "重启Jenkins失败: $_"
}

# 清理临时目录
Remove-Item -Path $TempDir -Recurse -Force

Write-Host "插件安装完成！请等待Jenkins重启完成。" -ForegroundColor Green 