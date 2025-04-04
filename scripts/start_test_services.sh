#!/bin/bash

# 检查系统资源
check_resources() {
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)
    MEM_USAGE=$(free | awk '/Mem/{printf("%.0f", $3/$2*100)}')
    
    if [ $CPU_USAGE -gt 80 ] || [ $MEM_USAGE -gt 80 ]; then
        echo "系统资源使用率过高，无法启动测试服务"
        echo "CPU使用率: $CPU_USAGE%"
        echo "内存使用率: $MEM_USAGE%"
        return 1
    fi
    return 0
}

# 停止其他非必要服务
stop_nonessential_services() {
    echo "停止非必要服务..."
    docker-compose stop mongodb jenkins
}

# 启动测试服务
start_test_services() {
    echo "启动测试服务..."
    docker-compose up -d playwright appium
    
    echo "等待服务启动..."
    sleep 10
    
    echo "测试服务状态："
    docker-compose ps playwright appium
}

# 主流程
echo "检查系统资源..."
if check_resources; then
    stop_nonessential_services
    start_test_services
else
    exit 1
fi 