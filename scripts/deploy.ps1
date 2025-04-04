# PowerShell部署脚本
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

param (
    [string]$env = "development"
)

# 配置信息
$remoteHost = "8.130.142.155"
$remoteUser = "root"
$projectRoot = "/data/projects/autotest"
$localPath = $PSScriptRoot

# 同步代码到远程服务器
Write-Host "正在同步代码到远程服务器..."
ssh ${remoteUser}@${remoteHost} "mkdir -p ${projectRoot}"
scp -r ../* ${remoteUser}@${remoteHost}:${projectRoot}/

# 在远程服务器执行部署命令
Write-Host "正在远程服务器上执行部署..."
ssh ${remoteUser}@${remoteHost} @'
    cd /data/projects/autotest

    # 检查并创建Python虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate

    # 安装依赖
    pip install -r requirements.txt

    # 执行数据库迁移
    python manage.py migrate

    # 重启服务
    if [ -f "/etc/supervisord.d/autotest.ini" ]; then
        supervisorctl restart autotest
    fi
'@

Write-Host "部署完成！" 