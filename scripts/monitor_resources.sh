#!/bin/bash

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# 检查系统资源
check_system_resources() {
    log "系统资源使用情况："
    echo "CPU使用率：$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"
    echo "内存使用：$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2}')"
    echo "磁盘使用：$(df -h / | awk 'NR==2{print $5}')"
}

# 检查Docker容器资源
check_docker_resources() {
    log "Docker容器资源使用情况："
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# 清理旧日志和临时文件
cleanup_old_files() {
    log "清理7天前的日志文件..."
    find /data/logs -type f -mtime +7 -delete
    
    log "清理Docker临时文件..."
    docker system prune -f
}

# 主循环
while true; do
    check_system_resources
    check_docker_resources
    
    # 如果资源使用超过阈值，发出警告
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)
    MEM_USAGE=$(free | awk '/Mem/{printf("%.0f", $3/$2*100)}')
    
    if [ $CPU_USAGE -gt 80 ]; then
        log "警告：CPU使用率过高 ($CPU_USAGE%)"
    fi
    
    if [ $MEM_USAGE -gt 80 ]; then
        log "警告：内存使用率过高 ($MEM_USAGE%)"
        cleanup_old_files
    fi
    
    sleep 300  # 每5分钟检查一次
done 