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

# 开始初始化
log "开始初始化远程服务器环境..."

# 创建必要的目录
ensure_directory "/data/projects/autotest"
ensure_directory "/data/logs/autotest"
ensure_directory "/data/backup/autotest"

# 下载并安装基础Python RPM包
log "安装基础Python RPM包..."
cd /tmp
wget https://mirrors.aliyun.com/centos/8-stream/BaseOS/x86_64/os/Packages/python3-3.6.8-47.el8.x86_64.rpm
wget https://mirrors.aliyun.com/centos/8-stream/BaseOS/x86_64/os/Packages/python3-libs-3.6.8-47.el8.x86_64.rpm
wget https://mirrors.aliyun.com/centos/8-stream/BaseOS/x86_64/os/Packages/python3-devel-3.6.8-47.el8.x86_64.rpm

rpm -ivh --nodeps python3-3.6.8-47.el8.x86_64.rpm
rpm -ivh --nodeps python3-libs-3.6.8-47.el8.x86_64.rpm
rpm -ivh --nodeps python3-devel-3.6.8-47.el8.x86_64.rpm

# 安装编译工具和依赖
log "安装编译工具和依赖..."
rpm -ivh --nodeps https://mirrors.aliyun.com/centos/8-stream/BaseOS/x86_64/os/Packages/gcc-8.5.0-17.el8.x86_64.rpm
rpm -ivh --nodeps https://mirrors.aliyun.com/centos/8-stream/BaseOS/x86_64/os/Packages/gcc-c++-8.5.0-17.el8.x86_64.rpm
rpm -ivh --nodeps https://mirrors.aliyun.com/centos/8-stream/BaseOS/x86_64/os/Packages/make-4.2.1-11.el8.x86_64.rpm
rpm -ivh --nodeps https://mirrors.aliyun.com/centos/8-stream/BaseOS/x86_64/os/Packages/wget-1.19.5-10.el8.x86_64.rpm

# 安装Python 3.10
log "开始安装Python 3.10..."
cd /tmp
wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz
tar xzf Python-3.10.0.tgz
cd Python-3.10.0
./configure --enable-optimizations --prefix=/usr/local/python3.10
make -j $(nproc)
make install
cd ..
rm -rf Python-3.10.0*

# 验证Python安装
log "验证Python安装..."
if ! /usr/local/python3.10/bin/python3 --version; then
    log "错误: Python3.10 安装失败"
    exit 1
fi

# 创建软链接
ln -sf /usr/local/python3.10/bin/python3 /usr/local/bin/python3
ln -sf /usr/local/python3.10/bin/pip3 /usr/local/bin/pip3

# 配置pip
log "配置pip..."
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
EOF

# 安装基础Python包
log "安装基础Python包..."
/usr/local/bin/python3 -m pip install --upgrade pip setuptools wheel virtualenv

# 安装Docker
log "安装Docker..."
yum install -y yum-utils

# 使用阿里云Docker源
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# 更新yum缓存
yum makecache

# 安装Docker
yum install -y docker-ce docker-ce-cli containerd.io

# 配置Docker镜像加速
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://mirror.ccs.tencentyun.com"
  ]
}
EOF

# 启动Docker服务
log "启动Docker服务..."
systemctl daemon-reload
systemctl start docker
systemctl enable docker
check_service docker

# 安装Docker Compose
log "安装Docker Compose..."
DOCKER_COMPOSE_VERSION="v2.20.0"

# 首先尝试通过yum安装
log "尝试通过yum安装docker-compose..."
if yum install -y docker-compose; then
    log "Docker Compose 通过yum安装成功"
else
    log "yum安装失败，尝试通过下载二进制文件安装..."
    COMPOSE_DOWNLOAD_URLS=(
        "https://mirror.ghproxy.com/https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)"
        "https://mirror.azure.cn/docker-toolbox/linux/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)"
        "https://download.fastgit.org/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)"
        "https://hub.fastgit.xyz/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)"
    )

    download_success=false
    for url in "${COMPOSE_DOWNLOAD_URLS[@]}"; do
        log "尝试从 ${url} 下载..."
        if curl -L -f "${url}" -o /usr/local/bin/docker-compose; then
            chmod +x /usr/local/bin/docker-compose
            log "Docker Compose 安装成功"
            download_success=true
            break
        fi
        log "下载失败，尝试下一个源..."
    done

    if [ "$download_success" = false ]; then
        log "错误: 所有下载源均失败，Docker Compose 安装失败"
        exit 1
    fi
fi

# 检查并备份系统Python依赖
backup_python_deps() {
    log "备份系统Python依赖..."
    # 创建备份目录
    mkdir -p /root/python_backup
    # 导出已安装的包列表
    if command -v python3.6 &> /dev/null; then
        python3.6 -m pip freeze > /root/python_backup/requirements_system.txt
    fi
}

# 移除旧版本Python
log "移除旧版本Python..."
yum remove -y python3 python3-devel python3-pip python3-setuptools

# 创建并配置虚拟环境
setup_virtualenv() {
    log "配置Python虚拟环境..."
    
    # 创建项目目录
    mkdir -p /data/projects/autotest/backend
    cd /data/projects/autotest/backend
    
    # 删除已存在的虚拟环境
    rm -rf venv
    
    # 创建新的虚拟环境
    python3 -m virtualenv venv
    
    # 激活虚拟环境并安装基本包
    source venv/bin/activate
    
    # 如果存在requirements.txt，则安装依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # 退出虚拟环境
    deactivate
}

# 执行Python环境配置
backup_python_deps

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