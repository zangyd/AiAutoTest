"""
文件管理器测试模块
"""
import os
import pytest
import tempfile
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile
import base64
import secrets

from core.utils.file_manager import FileManager

# 生成一个有效的Fernet密钥
TEST_SECRET_KEY = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def file_manager(temp_dir):
    """创建文件管理器实例"""
    return FileManager(
        base_path=temp_dir,
        secret_key=TEST_SECRET_KEY
    )

@pytest.fixture
def test_file_content():
    """测试文件内容"""
    return b"Hello, World!"

@pytest.fixture
def large_test_content():
    """大文件测试内容"""
    return b"Hello, World!" * 1000

@pytest.fixture
def upload_file(test_file_content):
    """模拟上传文件"""
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=test_file_content)
    mock_file.filename = "test.txt"
    return mock_file

@pytest.mark.asyncio
async def test_save_file_upload(file_manager, upload_file):
    """测试保存上传文件"""
    path = await file_manager.save_file(
        file=upload_file,
        filename="test.txt"
    )
    assert os.path.exists(path)
    with open(path, 'rb') as f:
        content = f.read()
    assert content == await upload_file.read()

@pytest.mark.asyncio
async def test_save_file_bytes(file_manager, test_file_content):
    """测试保存字节数据"""
    path = await file_manager.save_file(
        file=test_file_content,
        filename="test.bin"
    )
    assert os.path.exists(path)
    with open(path, 'rb') as f:
        content = f.read()
    assert content == test_file_content

@pytest.mark.asyncio
async def test_save_file_with_encryption(file_manager, test_file_content):
    """测试加密保存文件"""
    path = await file_manager.save_file(
        file=test_file_content,
        filename="encrypted.bin",
        encrypt=True
    )
    assert os.path.exists(path)
    with open(path, 'rb') as f:
        encrypted_content = f.read()
    assert encrypted_content != test_file_content

@pytest.mark.asyncio
async def test_save_file_with_compression(file_manager, large_test_content):
    """测试压缩保存文件"""
    path = await file_manager.save_file(
        file=large_test_content,
        filename="compressed.bin",
        compress=True
    )
    assert os.path.exists(path)
    with open(path, 'rb') as f:
        compressed_content = f.read()
    assert len(compressed_content) < len(large_test_content)

@pytest.mark.asyncio
async def test_read_file(file_manager, test_file_content):
    """测试读取文件"""
    filename = "test.txt"
    await file_manager.save_file(
        file=test_file_content,
        filename=filename
    )
    content = await file_manager.read_file(filename)
    assert content == test_file_content

@pytest.mark.asyncio
async def test_read_encrypted_file(file_manager, test_file_content):
    """测试读取加密文件"""
    filename = "encrypted.bin"
    await file_manager.save_file(
        file=test_file_content,
        filename=filename,
        encrypt=True
    )
    content = await file_manager.read_file(
        filename=filename,
        decrypt=True
    )
    assert content == test_file_content

@pytest.mark.asyncio
async def test_read_compressed_file(file_manager, test_file_content):
    """测试读取压缩文件"""
    filename = "compressed.bin"
    await file_manager.save_file(
        file=test_file_content,
        filename=filename,
        compress=True
    )
    content = await file_manager.read_file(
        filename=filename,
        decompress=True
    )
    assert content == test_file_content

@pytest.mark.asyncio
async def test_delete_file(file_manager, test_file_content):
    """测试删除文件"""
    filename = "to_delete.txt"
    path = await file_manager.save_file(
        file=test_file_content,
        filename=filename
    )
    assert os.path.exists(path)
    success = await file_manager.delete_file(filename)
    assert success
    assert not os.path.exists(path)

@pytest.mark.asyncio
async def test_list_files(file_manager, test_file_content):
    """测试列出文件"""
    # 创建测试文件
    filenames = ["test1.txt", "test2.txt", "test3.bin"]
    for filename in filenames:
        await file_manager.save_file(
            file=test_file_content,
            filename=filename
        )
    
    # 测试列出所有文件
    files = await file_manager.list_files()
    assert len(files) == 3
    assert set(files) == set(filenames)
    
    # 测试按模式匹配
    txt_files = await file_manager.list_files(pattern="*.txt")
    assert len(txt_files) == 2
    assert all(f.endswith('.txt') for f in txt_files)

@pytest.mark.asyncio
async def test_get_file_info(file_manager, test_file_content):
    """测试获取文件信息"""
    filename = "info_test.txt"
    await file_manager.save_file(
        file=test_file_content,
        filename=filename
    )
    
    info = await file_manager.get_file_info(filename)
    assert info["name"] == filename
    assert info["size"] == len(test_file_content)
    assert isinstance(info["created_time"], datetime)
    assert isinstance(info["modified_time"], datetime)
    assert info["mime_type"] == "text/plain"

@pytest.mark.asyncio
async def test_calculate_hash(file_manager, test_file_content):
    """测试计算文件哈希值"""
    filename = "hash_test.txt"
    await file_manager.save_file(
        file=test_file_content,
        filename=filename
    )
    
    # 测试不同哈希算法
    hash_md5 = await file_manager.calculate_hash(filename, "md5")
    hash_sha1 = await file_manager.calculate_hash(filename, "sha1")
    hash_sha256 = await file_manager.calculate_hash(filename, "sha256")
    
    assert len(hash_md5) == 32
    assert len(hash_sha1) == 40
    assert len(hash_sha256) == 64

@pytest.mark.asyncio
async def test_move_file(file_manager, test_file_content):
    """测试移动文件"""
    source = "source.txt"
    destination = "moved/dest.txt"
    
    # 创建源文件
    src_path = await file_manager.save_file(
        file=test_file_content,
        filename=source
    )
    assert os.path.exists(src_path)
    
    # 移动文件
    dst_path = await file_manager.move_file(source, destination)
    assert not os.path.exists(src_path)
    assert os.path.exists(dst_path)
    
    # 验证文件内容
    content = await file_manager.read_file(destination)
    assert content == test_file_content

@pytest.mark.asyncio
async def test_copy_file(file_manager, test_file_content):
    """测试复制文件"""
    source = "source.txt"
    destination = "copied/dest.txt"
    
    # 创建源文件
    src_path = await file_manager.save_file(
        file=test_file_content,
        filename=source
    )
    assert os.path.exists(src_path)
    
    # 复制文件
    dst_path = await file_manager.copy_file(source, destination)
    assert os.path.exists(src_path)
    assert os.path.exists(dst_path)
    
    # 验证两个文件的内容相同
    src_content = await file_manager.read_file(source)
    dst_content = await file_manager.read_file(destination)
    assert src_content == dst_content == test_file_content

@pytest.mark.asyncio
async def test_file_not_found(file_manager):
    """测试文件不存在的情况"""
    with pytest.raises(FileNotFoundError):
        await file_manager.read_file("nonexistent.txt")
    
    with pytest.raises(FileNotFoundError):
        await file_manager.get_file_info("nonexistent.txt")
    
    with pytest.raises(FileNotFoundError):
        await file_manager.calculate_hash("nonexistent.txt")
    
    with pytest.raises(FileNotFoundError):
        await file_manager.move_file("nonexistent.txt", "dest.txt")
    
    with pytest.raises(FileNotFoundError):
        await file_manager.copy_file("nonexistent.txt", "dest.txt")

@pytest.mark.asyncio
async def test_invalid_encryption(file_manager, test_file_content):
    """测试无效的加密操作"""
    # 创建一个没有加密密钥的文件管理器
    no_key_manager = FileManager(base_path=file_manager.base_path)
    
    with pytest.raises(ValueError):
        await no_key_manager.save_file(
            file=test_file_content,
            filename="test.txt",
            encrypt=True
        )
    
    # 保存加密文件
    filename = "encrypted.bin"
    await file_manager.save_file(
        file=test_file_content,
        filename=filename,
        encrypt=True
    )
    
    # 尝试用不同的密钥解密
    with pytest.raises(ValueError):
        await no_key_manager.read_file(
            filename=filename,
            decrypt=True
        ) 