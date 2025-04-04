#!/bin/bash

echo "开始初始化远程服务器环境..."

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

# 创建Python虚拟环境
cd /data/projects/autotest/backend
python3 -m venv venv
source venv/bin/activate

# 安装项目依赖
pip install --upgrade pip
for req in requirements/*.txt; do
    pip install -r "$req"
done

# 安装Supervisor
yum install -y supervisor
systemctl start supervisord
systemctl enable supervisord

# 创建supervisor配置
cat > /etc/supervisord.d/autotest.ini << EOF
[program:autotest]
directory=/data/projects/autotest/backend
command=/data/projects/autotest/backend/venv/bin/python manage.py runserver 0.0.0.0:8000
autostart=true
autorestart=true
stderr_logfile=/data/logs/autotest/err.log
stdout_logfile=/data/logs/autotest/out.log
environment=PYTHONPATH="/data/projects/autotest/backend"
EOF

# 重启supervisor
supervisorctl reread
supervisorctl update

echo "远程服务器初始化完成！" 