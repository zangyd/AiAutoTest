import os
import sys
import time
import json
import socket
import requests
import docker
from pathlib import Path

class HealthChecker:
    def __init__(self):
        """初始化健康检查器"""
        self.project_root = Path(__file__).parent.parent
        self.services = {
            "frontend": {"port": 3000, "url": "http://localhost:3000/health"},
            "backend": {"port": 8000, "url": "http://localhost:8000/health"},
            "jenkins": {"port": 8080, "url": "http://localhost:8080/login"},
        }
        self.docker_client = docker.from_env()

    def check_port(self, port):
        """检查端口是否可用"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = sock.connect_ex(('localhost', port))
            return result == 0
        finally:
            sock.close()

    def check_http_service(self, url):
        """检查HTTP服务是否可用"""
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def check_docker_containers(self):
        """检查Docker容器状态"""
        print("检查Docker容器状态...")
        try:
            containers = self.docker_client.containers.list()
            for container in containers:
                status = container.status
                name = container.name
                print(f"容器 {name}: {status}")
                if status != "running":
                    return False
            return True
        except docker.errors.DockerException as e:
            print(f"Docker容器检查失败: {str(e)}")
            return False

    def check_services(self):
        """检查所有服务状态"""
        print("检查服务状态...")
        all_healthy = True
        
        for service, config in self.services.items():
            print(f"\n检查 {service} 服务:")
            
            # 检查端口
            port_available = self.check_port(config["port"])
            print(f"- 端口 {config['port']}: {'✓' if port_available else '✗'}")
            
            # 检查HTTP服务
            http_available = self.check_http_service(config["url"])
            print(f"- HTTP服务: {'✓' if http_available else '✗'}")
            
            if not (port_available and http_available):
                all_healthy = False
        
        return all_healthy

    def check_disk_space(self):
        """检查磁盘空间"""
        print("\n检查磁盘空间...")
        try:
            if sys.platform == "win32":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    str(self.project_root), None, None, ctypes.pointer(free_bytes))
                free_gb = free_bytes.value / (1024**3)
            else:
                import os
                st = os.statvfs(str(self.project_root))
                free_gb = (st.f_bavail * st.f_frsize) / (1024**3)
            
            print(f"可用空间: {free_gb:.2f} GB")
            return free_gb > 10  # 要求至少10GB可用空间
            
        except Exception as e:
            print(f"磁盘空间检查失败: {str(e)}")
            return False

    def check_logs(self):
        """检查日志文件"""
        print("\n检查日志文件...")
        log_dir = self.project_root / "logs"
        
        if not log_dir.exists():
            print("日志目录不存在")
            return False
            
        try:
            # 检查日志文件权限和大小
            for log_file in log_dir.glob("*.log"):
                size_mb = log_file.stat().st_size / (1024*1024)
                if size_mb > 100:  # 日志文件超过100MB报警
                    print(f"警告: {log_file.name} 大小超过100MB ({size_mb:.2f}MB)")
                    
            return True
            
        except Exception as e:
            print(f"日志检查失败: {str(e)}")
            return False

    def run_health_check(self):
        """运行所有健康检查"""
        print("开始健康检查...")
        print("-" * 50)
        
        checks = {
            "Docker容器": self.check_docker_containers(),
            "服务状态": self.check_services(),
            "磁盘空间": self.check_disk_space(),
            "日志文件": self.check_logs()
        }
        
        print("\n健康检查结果汇总:")
        print("-" * 50)
        all_healthy = True
        
        for check, result in checks.items():
            status = "✓" if result else "✗"
            print(f"{check}: {status}")
            if not result:
                all_healthy = False
        
        print("-" * 50)
        if all_healthy:
            print("所有检查通过 ✓")
            return 0
        else:
            print("存在检查未通过项 ✗")
            return 1

def main():
    """主函数"""
    checker = HealthChecker()
    return checker.run_health_check()

if __name__ == "__main__":
    sys.exit(main()) 