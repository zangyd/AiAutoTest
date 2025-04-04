import pytest
import os
import subprocess
import docker
import requests
import time
import json
from pathlib import Path

class TestCICDEnvironment:
    """CI/CD环境测试类"""
    
    def setup_method(self):
        """测试前准备"""
        # 设置Jenkins相关配置
        self.jenkins_url = "http://localhost:8080"
        self.jenkins_user = os.getenv("JENKINS_USER", "admin")
        self.jenkins_token = os.getenv("JENKINS_TOKEN", "")
        
        # Docker客户端
        self.docker_client = docker.from_env()
        
        # 项目根目录
        self.project_root = Path(__file__).parent.parent.parent

    def test_jenkins_environment(self):
        """测试Jenkins环境配置"""
        try:
            # 测试Jenkins服务是否运行
            response = requests.get(f"{self.jenkins_url}/login")
            assert response.status_code == 200, "Jenkins服务未运行"
            
            # 测试Jenkins API访问
            auth = (self.jenkins_user, self.jenkins_token)
            api_response = requests.get(f"{self.jenkins_url}/api/json", auth=auth)
            assert api_response.status_code == 200, "Jenkins API访问失败"
            
            # 验证必要插件是否安装
            plugins_response = requests.get(f"{self.jenkins_url}/pluginManager/api/json", auth=auth)
            plugins = json.loads(plugins_response.text)["plugins"]
            required_plugins = {
                "git", "pipeline", "docker-workflow", "python", "junit"
            }
            installed_plugins = {p["shortName"] for p in plugins}
            missing_plugins = required_plugins - installed_plugins
            assert not missing_plugins, f"缺少必要的Jenkins插件: {missing_plugins}"
            
        except requests.exceptions.ConnectionError:
            pytest.fail("无法连接到Jenkins服务")

    def test_docker_environment(self):
        """测试Docker环境配置"""
        try:
            # 测试Docker服务状态
            assert self.docker_client.ping(), "Docker服务未运行"
            
            # 测试Docker镜像构建
            dockerfile_path = self.project_root / "Dockerfile"
            assert dockerfile_path.exists(), "Dockerfile不存在"
            
            # 测试docker-compose配置
            compose_path = self.project_root / "docker-compose.yml"
            assert compose_path.exists(), "docker-compose.yml不存在"
            
            # 测试基础镜像拉取
            required_images = ["python:3.10", "node:16"]
            for image in required_images:
                try:
                    self.docker_client.images.pull(image)
                except docker.errors.ImageNotFound:
                    pytest.fail(f"无法拉取基础镜像: {image}")
                
            # 验证Docker网络配置
            networks = self.docker_client.networks.list()
            assert any(n.name == "bridge" for n in networks), "Docker默认网络配置异常"
            
        except docker.errors.DockerException as e:
            pytest.fail(f"Docker环境测试失败: {str(e)}")

    def test_deployment_scripts(self):
        """测试部署脚本"""
        # 测试部署脚本是否存在
        deploy_script = self.project_root / "scripts" / "deploy.py"
        assert deploy_script.exists(), "部署脚本不存在"
        
        # 测试环境检查脚本
        env_check_script = self.project_root / "scripts" / "check_environment.py"
        assert env_check_script.exists(), "环境检查脚本不存在"
        
        # 测试服务健康检查脚本
        health_check_script = self.project_root / "scripts" / "health_check.py"
        assert health_check_script.exists(), "健康检查脚本不存在"
        
        try:
            # 测试环境检查脚本执行
            result = subprocess.run(
                ["python", str(env_check_script)],
                capture_output=True,
                text=True,
                check=True
            )
            assert result.returncode == 0, "环境检查脚本执行失败"
            
            # 测试健康检查脚本执行
            result = subprocess.run(
                ["python", str(health_check_script)],
                capture_output=True,
                text=True,
                check=True
            )
            assert result.returncode == 0, "健康检查脚本执行失败"
            
        except subprocess.CalledProcessError as e:
            pytest.fail(f"部署脚本测试失败: {str(e)}")

    def test_pipeline_configuration(self):
        """测试流水线配置"""
        # 测试Jenkinsfile是否存在
        jenkins_file = self.project_root / "Jenkinsfile"
        assert jenkins_file.exists(), "Jenkinsfile不存在"
        
        # 测试流水线语法
        try:
            result = subprocess.run(
                ["jenkins-cli", "declarative-linter", str(jenkins_file)],
                capture_output=True,
                text=True,
                check=True
            )
            assert result.returncode == 0, "Jenkinsfile语法检查失败"
        except FileNotFoundError:
            pytest.skip("jenkins-cli工具未安装，跳过流水线语法检查")
        except subprocess.CalledProcessError as e:
            pytest.fail(f"流水线配置测试失败: {str(e)}")

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 