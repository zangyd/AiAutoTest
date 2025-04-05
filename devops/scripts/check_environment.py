import sys
import os
import platform
import subprocess
import docker
import requests
import json

def check_python_environment():
    """检查Python环境"""
    print("检查Python环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major != 3 or python_version.minor < 10:
        raise RuntimeError(f"Python版本要求3.10+，当前版本: {sys.version}")
    
    # 检查必要的Python包
    required_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "pytest",
        "requests", "docker", "python-jenkins"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            raise RuntimeError(f"缺少必要的Python包: {package}")
    
    print("Python环境检查通过 ✓")

def check_node_environment():
    """检查Node.js环境"""
    print("检查Node.js环境...")
    
    try:
        # 检查Node.js版本
        result = subprocess.run(
            ["node", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        version = result.stdout.strip()
        if not version.startswith("v16"):
            raise RuntimeError(f"Node.js版本要求16.x，当前版本: {version}")
        
        # 检查npm版本
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print("Node.js环境检查通过 ✓")
        
    except subprocess.CalledProcessError:
        raise RuntimeError("Node.js未安装或配置不正确")
    except FileNotFoundError:
        raise RuntimeError("找不到node或npm命令")

def check_docker_environment():
    """检查Docker环境"""
    print("检查Docker环境...")
    
    try:
        client = docker.from_env()
        client.ping()
        
        # 检查必要的基础镜像
        required_images = ["python:3.10", "node:16"]
        for image in required_images:
            try:
                client.images.get(image)
            except docker.errors.ImageNotFound:
                print(f"警告: 未找到镜像 {image}，将尝试拉取")
                client.images.pull(image)
        
        print("Docker环境检查通过 ✓")
        
    except docker.errors.DockerException as e:
        raise RuntimeError(f"Docker环境检查失败: {str(e)}")

def check_jenkins_environment():
    """检查Jenkins环境"""
    print("检查Jenkins环境...")
    
    jenkins_url = os.getenv("JENKINS_URL", "http://localhost:8090")
    try:
        response = requests.get(f"{jenkins_url}/login")
        if response.status_code != 200:
            raise RuntimeError("Jenkins服务未运行或无法访问")
        
        print("Jenkins环境检查通过 ✓")
        
    except requests.exceptions.ConnectionError:
        raise RuntimeError("无法连接到Jenkins服务")

def main():
    """主函数"""
    try:
        print("开始环境检查...")
        print("-" * 50)
        
        # 系统信息
        print(f"操作系统: {platform.system()} {platform.release()}")
        print(f"Python版本: {sys.version}")
        print("-" * 50)
        
        # 环境检查
        check_python_environment()
        check_node_environment()
        check_docker_environment()
        check_jenkins_environment()
        
        print("-" * 50)
        print("所有环境检查通过 ✓")
        return 0
        
    except Exception as e:
        print(f"环境检查失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 