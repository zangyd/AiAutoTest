"""
文件处理工具模块，提供文件操作、压缩、加密等功能。
"""
import os
import shutil
import hashlib
import gzip
import base64
from pathlib import Path
from typing import Union, List, Optional, BinaryIO
from datetime import datetime
import aiofiles
import aiofiles.os
from cryptography.fernet import Fernet
from fastapi import UploadFile
import magic

class FileManager:
    """文件管理工具类，提供异步文件操作功能"""
    
    def __init__(self, base_path: str, secret_key: Optional[str] = None):
        """
        初始化文件管理器
        
        Args:
            base_path: 基础路径
            secret_key: 加密密钥(可选)，如果提供则必须是32字节的url-safe base64编码字符串
        """
        self.base_path = Path(base_path)
        self.secret_key = secret_key
        
        if secret_key:
            try:
                # 如果密钥不是base64编码，则进行编码
                if not self._is_base64(secret_key):
                    # 确保密钥是32字节
                    raw_key = secret_key.encode()[:32].ljust(32, b'\0')
                    key = base64.urlsafe_b64encode(raw_key)
                else:
                    key = secret_key.encode()
                    # 尝试解码以验证格式
                    base64.urlsafe_b64decode(key)
                self._fernet = Fernet(key)
            except Exception as e:
                raise ValueError(f"无效的加密密钥: {str(e)}")
        else:
            self._fernet = None
        
        # 创建基础目录
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def _is_base64(self, s: str) -> bool:
        """
        检查字符串是否是base64编码
        
        Args:
            s: 要检查的字符串
            
        Returns:
            bool: 是否是base64编码
        """
        try:
            # 检查是否是有效的base64编码
            decoded = base64.urlsafe_b64decode(s.encode())
            return len(decoded) == 32
        except Exception:
            return False
        
    async def save_file(self, 
                       file: Union[UploadFile, BinaryIO, bytes], 
                       filename: str,
                       encrypt: bool = False,
                       compress: bool = False) -> str:
        """
        保存文件
        
        Args:
            file: 要保存的文件对象
            filename: 文件名
            encrypt: 是否加密
            compress: 是否压缩
            
        Returns:
            str: 保存后的文件路径
        """
        file_path = self.base_path / filename
        
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 处理不同类型的输入
        if isinstance(file, UploadFile):
            content = await file.read()
        elif isinstance(file, bytes):
            content = file
        else:
            content = file.read()
            
        # 压缩处理
        if compress:
            content = gzip.compress(content)
            
        # 加密处理
        if encrypt:
            if not self._fernet:
                raise ValueError("未配置加密密钥")
            content = self._fernet.encrypt(content)
            
        # 异步写入文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
            
        return str(file_path)
        
    async def read_file(self,
                       filename: str,
                       decrypt: bool = False,
                       decompress: bool = False) -> bytes:
        """
        读取文件
        
        Args:
            filename: 文件名
            decrypt: 是否解密
            decompress: 是否解压
            
        Returns:
            bytes: 文件内容
        """
        file_path = self.base_path / filename
        
        if not await aiofiles.os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {filename}")
            
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
            
        # 解密处理
        if decrypt:
            if not self._fernet:
                raise ValueError("未配置解密密钥")
            content = self._fernet.decrypt(content)
            
        # 解压处理
        if decompress:
            content = gzip.decompress(content)
            
        return content
        
    async def delete_file(self, filename: str) -> bool:
        """
        删除文件
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否删除成功
        """
        file_path = self.base_path / filename
        
        if await aiofiles.os.path.exists(file_path):
            await aiofiles.os.remove(file_path)
            return True
        return False
        
    async def list_files(self, 
                        directory: str = "",
                        pattern: str = "*") -> List[str]:
        """
        列出目录下的文件
        
        Args:
            directory: 相对目录路径
            pattern: 文件匹配模式
            
        Returns:
            List[str]: 文件列表
        """
        dir_path = self.base_path / directory
        if not await aiofiles.os.path.exists(dir_path):
            return []
            
        files = []
        entries = await aiofiles.os.scandir(dir_path)
        for entry in entries:
            entry_stat = await aiofiles.os.stat(entry.path)
            if entry_stat.st_mode & 0o100000 and Path(entry.name).match(pattern):  # 检查是否是普通文件
                files.append(entry.name)
        return files
        
    async def get_file_info(self, filename: str) -> dict:
        """
        获取文件信息
        
        Args:
            filename: 文件名
            
        Returns:
            dict: 文件信息
        """
        file_path = self.base_path / filename
        
        if not await aiofiles.os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {filename}")
            
        stat = await aiofiles.os.stat(file_path)
        
        # 使用python-magic检测文件类型
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(str(file_path))
        
        return {
            "name": filename,
            "size": stat.st_size,
            "created_time": datetime.fromtimestamp(stat.st_ctime),
            "modified_time": datetime.fromtimestamp(stat.st_mtime),
            "mime_type": file_type
        }
        
    async def calculate_hash(self, 
                           filename: str,
                           algorithm: str = 'sha256') -> str:
        """
        计算文件哈希值
        
        Args:
            filename: 文件名
            algorithm: 哈希算法(md5/sha1/sha256)
            
        Returns:
            str: 哈希值
        """
        file_path = self.base_path / filename
        
        if not await aiofiles.os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {filename}")
            
        hash_obj = hashlib.new(algorithm)
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_obj.update(chunk)
                
        return hash_obj.hexdigest()
        
    async def move_file(self, 
                       source: str,
                       destination: str) -> str:
        """
        移动文件
        
        Args:
            source: 源文件名
            destination: 目标文件名
            
        Returns:
            str: 新的文件路径
        """
        src_path = self.base_path / source
        dst_path = self.base_path / destination
        
        if not await aiofiles.os.path.exists(src_path):
            raise FileNotFoundError(f"源文件不存在: {source}")
            
        # 确保目标目录存在
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        await aiofiles.os.rename(src_path, dst_path)
        return str(dst_path)
        
    async def copy_file(self,
                       source: str,
                       destination: str) -> str:
        """
        复制文件
        
        Args:
            source: 源文件名
            destination: 目标文件名
            
        Returns:
            str: 新的文件路径
        """
        src_path = self.base_path / source
        dst_path = self.base_path / destination
        
        if not await aiofiles.os.path.exists(src_path):
            raise FileNotFoundError(f"源文件不存在: {source}")
            
        # 确保目标目录存在
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 读取源文件内容
        async with aiofiles.open(src_path, 'rb') as src_file:
            content = await src_file.read()
            
        # 写入目标文件
        async with aiofiles.open(dst_path, 'wb') as dst_file:
            await dst_file.write(content)
            
        return str(dst_path) 