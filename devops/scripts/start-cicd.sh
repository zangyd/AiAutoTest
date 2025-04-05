#!/bin/bash

# 确保目录存在
mkdir -p jenkins/casc
mkdir -p prometheus
mkdir -p logstash/pipeline

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "Docker未运行，正在启动..."
    systemctl start docker
fi

# 构建并启动服务
docker-compose -f docker-compose-monitor.yml build
docker-compose -f docker-compose-monitor.yml up -d

# 等待Jenkins启动
echo "等待Jenkins启动..."
until $(curl --output /dev/null --silent --head --fail http://localhost:8080); do
    printf '.'
    sleep 5
done

# 获取Jenkins初始管理员密码
echo "Jenkins初始管理员密码："
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# 显示服务访问地址
echo "
服务访问地址：
Jenkins: http://localhost:8080
Prometheus: http://localhost:9090
Grafana: http://localhost:3000
Kibana: http://localhost:5601
"

# 检查服务状态
docker-compose -f docker-compose-monitor.yml ps 