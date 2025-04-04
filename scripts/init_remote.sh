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
yum install -y git python3 python3-devel gcc make openssl-devel bzip2-devel libffi-devel

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

# 移除旧版本Python
yum remove -y python3

# 安装编译Python所需的依赖
yum groupinstall -y "Development Tools"
yum install -y openssl-devel bzip2-devel libffi-devel xz-devel

# 安装Python 3.10
install_python() {
    echo "开始安装Python 3.10..."
    
    # 安装编译依赖
    yum groupinstall -y "Development Tools"
    yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel
    
    # 下载Python源码（使用国内镜像）
    cd /tmp
    wget https://mirrors.huaweicloud.com/python/3.10.13/Python-3.10.13.tgz
    tar xzf Python-3.10.13.tgz
    cd Python-3.10.13
    
    # 配置和编译安装
    ./configure --enable-optimizations
    make -j $(nproc)
    make install
    
    # 创建软链接
    ln -sf /usr/local/bin/python3.10 /usr/local/bin/python3
    ln -sf /usr/local/bin/pip3.10 /usr/local/bin/pip3
    
    # 安装pip
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --force-reinstall
    
    # 配置pip源为阿里云
    mkdir -p ~/.pip
    cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
EOF
    
    # 升级pip
    pip3 install --upgrade pip
    
    # 安装virtualenv
    pip3 install virtualenv
    
    cd -
    rm -rf /tmp/Python-3.10.13*
}

# 创建并配置虚拟环境
setup_virtualenv() {
    echo "配置Python虚拟环境..."
    
    # 创建项目目录
    mkdir -p /data/projects/autotest/backend
    cd /data/projects/autotest/backend
    
    # 删除已存在的虚拟环境
    rm -rf venv
    
    # 创建新的虚拟环境
    python3 -m virtualenv venv
    
    # 激活虚拟环境并安装基本包
    source venv/bin/activate
    pip install --upgrade pip
    pip install wheel setuptools
    
    # 如果存在requirements.txt，则安装依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # 退出虚拟环境
    deactivate
}

# 执行安装和配置
install_python
setup_virtualenv

echo "Python环境配置完成！"

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