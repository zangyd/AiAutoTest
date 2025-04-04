# 远程服务器初始化脚本
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$remoteHost = "8.130.142.155"
$remoteUser = "root"

Write-Host "开始初始化远程服务器环境..."

# 在远程服务器执行初始化命令
ssh ${remoteUser}@${remoteHost} @'
    # 更新系统包
    yum update -y
    
    # 安装基础工具
    yum install -y git python3 python3-devel gcc make openssl-devel bzip2-devel libffi-devel
    
    # 安装Docker
    yum install -y yum-utils
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    yum install -y docker-ce docker-ce-cli containerd.io
    
    # 启动Docker服务
    systemctl start docker
    systemctl enable docker
    
    # 安装Docker Compose
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # 创建项目目录
    mkdir -p /data/projects/autotest
    mkdir -p /data/logs/autotest
    
    # 安装Supervisor
    yum install -y supervisor
    systemctl start supervisord
    systemctl enable supervisord
    
    # 创建supervisor配置
    cat > /etc/supervisord.d/autotest.ini << EOF
[program:autotest]
directory=/data/projects/autotest
command=/data/projects/autotest/venv/bin/python manage.py runserver 0.0.0.0:8000
autostart=true
autorestart=true
stderr_logfile=/data/logs/autotest/err.log
stdout_logfile=/data/logs/autotest/out.log
environment=PYTHONPATH="/data/projects/autotest"
EOF
    
    # 重启supervisor
    supervisorctl reread
    supervisorctl update
    
    echo "远程服务器初始化完成！"
'@

Write-Host "初始化完成！" 