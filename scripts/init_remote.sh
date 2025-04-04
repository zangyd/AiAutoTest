#!/bin/bash

# 错误处理
set -e
trap 'echo "错误发生在第 $LINENO 行"; exit 1' ERR

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log "错误: 命令 $1 未找到"
        return 1
    fi
}

# 检查目录是否存在，不存在则创建
ensure_directory() {
    if [ ! -d "$1" ]; then
        log "创建目录: $1"
        mkdir -p "$1"
    fi
}

# 检查服务状态
check_service() {
    if ! systemctl is-active $1 &> /dev/null; then
        log "错误: 服务 $1 未运行"
        return 1
    fi
}

log "开始初始化远程服务器环境..."

# 创建必要的目录
ensure_directory "/data/projects/autotest"
ensure_directory "/data/logs/autotest"
ensure_directory "/data/backup/autotest"

# 更新系统包
log "更新系统包..."
yum update -y

# 安装基础工具
log "安装基础工具..."
yum install -y git gcc make openssl-devel bzip2-devel libffi-devel wget

# 安装Python 3.10
log "安装Python 3.10..."
PYTHON_VERSION="3.10.13"
cd /tmp
wget https://npm.taobao.org/mirrors/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz || \
wget https://repo.huaweicloud.com/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz || \
wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz

tar xzf Python-${PYTHON_VERSION}.tgz
cd Python-${PYTHON_VERSION}
./configure --enable-optimizations
make altinstall
cd ..
rm -rf Python-${PYTHON_VERSION}*

# 创建软链接
ln -sf /usr/local/bin/python3.10 /usr/local/bin/python3
ln -sf /usr/local/bin/pip3.10 /usr/local/bin/pip3

# 验证Python版本
log "Python版本信息:"
python3 --version

# 安装Docker
log "安装Docker..."
yum install -y yum-utils
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
log "启动Docker服务..."
systemctl start docker
systemctl enable docker
check_service docker

# 安装Docker Compose
log "安装Docker Compose..."
DOCKER_COMPOSE_VERSION="v2.20.0"
# 使用国内镜像源
curl -L "https://get.daocloud.io/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose || \
curl -L "https://mirror.azure.cn/docker-toolbox/linux/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose || \
curl -L "https://ghproxy.com/https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

if [ $? -eq 0 ]; then
    chmod +x /usr/local/bin/docker-compose
    log "Docker Compose 安装成功"
else
    log "错误: Docker Compose 安装失败"
    exit 1
fi

# 配置Python环境
log "配置Python环境..."
cd /data/projects/autotest/backend

# 安装venv模块
python3 -m pip install --upgrade pip virtualenv

# 检查并创建虚拟环境
if [ ! -d "venv" ]; then
    python3 -m virtualenv venv
fi

source venv/bin/activate

# 配置pip源为阿里云
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
EOF

# 安装项目依赖
log "安装项目依赖..."
pip install --upgrade pip
if [ -d "requirements" ]; then
    for req in requirements/*.txt; do
        if [ -f "$req" ]; then
            log "安装依赖: $req"
            pip install -r "$req"
        fi
    done
else
    log "警告: requirements目录不存在"
fi

# 安装Supervisor
log "安装Supervisor..."
yum install -y supervisor
systemctl start supervisord
systemctl enable supervisord
check_service supervisord

# 创建supervisor配置
log "配置Supervisor..."
cat > /etc/supervisord.d/autotest.ini << EOF
[program:autotest]
directory=/data/projects/autotest/backend
command=/data/projects/autotest/backend/venv/bin/python manage.py runserver 0.0.0.0:8000
autostart=true
autorestart=true
stderr_logfile=/data/logs/autotest/err.log
stdout_logfile=/data/logs/autotest/out.log
environment=PYTHONPATH="/data/projects/autotest/backend"
user=root
numprocs=1
startsecs=10
stopsignal=TERM
stopwaitsecs=10
EOF

# 更新supervisor配置
log "更新Supervisor配置..."
supervisorctl reread
supervisorctl update

# 检查服务状态
log "检查服务状态..."
if ! supervisorctl status autotest | grep -q "RUNNING"; then
    log "警告: autotest服务未正常运行"
fi

# 创建数据库备份目录
ensure_directory "/data/backup/autotest/db"

# 设置定时任务
log "配置定时任务..."
(crontab -l 2>/dev/null; echo "0 2 * * * /data/projects/autotest/backend/scripts/backup_db.sh") | crontab -

log "远程服务器初始化完成！"

# 输出环境信息
log "环境信息:"
python3 --version
docker --version
docker-compose --version
supervisord --version

# 检查服务状态
log "服务状态:"
systemctl status docker --no-pager
systemctl status supervisord --no-pager
supervisorctl status autotest 