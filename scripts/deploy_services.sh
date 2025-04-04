#!/bin/bash

# 错误处理
set -e
trap 'echo "错误发生在第 $LINENO 行"; exit 1' ERR

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# 检查Docker服务
log "检查Docker服务..."
if ! systemctl is-active docker &> /dev/null; then
    log "启动Docker服务..."
    systemctl start docker
fi

# 创建必要的目录
mkdir -p /data/{mysql,mongodb,redis,jenkins,logs}

# 创建docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  mysql:
    image: mysql:5.7
    container_name: mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: autotest
    volumes:
      - /data/mysql:/var/lib/mysql
    ports:
      - "3306:3306"
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 500M
        reservations:
          cpus: '0.1'
          memory: 200M

  mongodb:
    image: mongo:4.4
    container_name: mongodb
    restart: unless-stopped
    volumes:
      - /data/mongodb:/data/db
    ports:
      - "27017:27017"
    deploy:
      resources:
        limits:
          cpus: '0.3'
          memory: 300M
        reservations:
          cpus: '0.1'
          memory: 100M
    command: ["--wiredTigerCacheSizeGB", "0.25"]

  redis:
    image: redis:6.2
    container_name: redis
    restart: unless-stopped
    volumes:
      - /data/redis:/data
    ports:
      - "6379:6379"
    deploy:
      resources:
        limits:
          cpus: '0.1'
          memory: 100M
        reservations:
          cpus: '0.05'
          memory: 50M
    command: ["redis-server", "--maxmemory", "100mb", "--maxmemory-policy", "allkeys-lru"]

  jenkins:
    image: jenkins/jenkins:lts-jdk11
    container_name: jenkins
    restart: unless-stopped
    environment:
      JAVA_OPTS: "-Xmx500m -Xms200m"
    volumes:
      - /data/jenkins:/var/jenkins_home
    ports:
      - "8080:8080"
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 500M
        reservations:
          cpus: '0.1'
          memory: 200M

  playwright:
    image: mcr.microsoft.com/playwright:v1.35.0
    container_name: playwright
    restart: "no"  # 按需启动
    deploy:
      resources:
        limits:
          cpus: '0.1'
          memory: 100M
        reservations:
          cpus: '0.05'
          memory: 50M

  appium:
    image: appium/appium:latest
    container_name: appium
    restart: "no"  # 按需启动
    deploy:
      resources:
        limits:
          cpus: '0.1'
          memory: 100M
        reservations:
          cpus: '0.05'
          memory: 50M
EOF

# 分阶段启动服务
echo "启动核心服务..."
docker-compose up -d mysql redis

echo "等待30秒..."
sleep 30

echo "启动MongoDB和Jenkins..."
docker-compose up -d mongodb jenkins

# 设置监控脚本
chmod +x monitor_resources.sh
nohup ./monitor_resources.sh > /data/logs/monitor.log 2>&1 &

echo "服务部署完成！"
echo "请访问 http://localhost:8080 查看Jenkins状态"
echo "初始Jenkins密码："
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# 输出服务访问信息
log "服务访问信息:"
echo "MySQL: localhost:3306"
echo "MongoDB: localhost:27017"
echo "Redis: localhost:6379"
echo "Jenkins: http://localhost:8080"
echo "Appium: localhost:4723" 