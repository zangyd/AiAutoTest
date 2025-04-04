"""
Appium服务器管理类
"""
import os
import time
import socket
import subprocess
import logging
from typing import Optional
from ..config.appium_config import APPIUM_SERVER

logger = logging.getLogger(__name__)

class AppiumServer:
    """Appium服务器管理类"""
    
    def __init__(self):
        """初始化Appium服务器管理器"""
        self.host = APPIUM_SERVER['host']
        self.port = APPIUM_SERVER['port']
        self.process: Optional[subprocess.Popen] = None
        
    def start_server(self, timeout: int = 30) -> bool:
        """
        启动Appium服务器
        
        Args:
            timeout: 启动超时时间(秒)
            
        Returns:
            bool: 服务器是否成功启动
        """
        try:
            # 检查端口是否被占用
            if self._is_port_in_use():
                logger.warning(f"端口{self.port}已被占用，尝试终止现有进程")
                self._kill_process_on_port()
                
            # 启动Appium服务器
            cmd = f"appium -a {self.host} -p {self.port}"
            self.process = subprocess.Popen(
                cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8'
            )
            
            # 等待服务器启动
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self._is_server_running():
                    logger.info(f"Appium服务器启动成功: {self.host}:{self.port}")
                    return True
                time.sleep(1)
                
            logger.error(f"Appium服务器启动超时: {timeout}秒")
            return False
            
        except Exception as e:
            logger.error(f"启动Appium服务器失败: {str(e)}")
            return False
            
    def stop_server(self):
        """停止Appium服务器"""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=10)
                self.process = None
                logger.info("Appium服务器已停止")
                
            # 确保端口被释放
            if self._is_port_in_use():
                self._kill_process_on_port()
                
        except Exception as e:
            logger.error(f"停止Appium服务器失败: {str(e)}")
            raise
            
    def _is_server_running(self) -> bool:
        """检查服务器是否正在运行"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((self.host, self.port))
                return result == 0
        except:
            return False
            
    def _is_port_in_use(self) -> bool:
        """检查端口是否被占用"""
        return self._is_server_running()
        
    def _kill_process_on_port(self):
        """终止占用端口的进程"""
        try:
            if os.name == 'nt':  # Windows
                cmd = f"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr {self.port}') do taskkill /F /PID %a"
                subprocess.run(cmd, shell=True)
            else:  # Linux/Mac
                cmd = f"lsof -i tcp:{self.port} | grep LISTEN | awk '{{print $2}}' | xargs kill -9"
                subprocess.run(cmd, shell=True)
        except Exception as e:
            logger.error(f"终止进程失败: {str(e)}")
            
    def __enter__(self):
        """上下文管理器入口"""
        self.start_server()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop_server() 