"""
验证码功能的单元测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import base64
import io
from PIL import Image
import re

from core.auth.captcha import CaptchaManager

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_cache_manager():
    """创建模拟的缓存管理器"""
    mock = AsyncMock()
    mock.set.return_value = True
    mock.get.return_value = "1234"
    mock.exists.return_value = True
    mock.delete.return_value = 1
    mock.keys.return_value = ["captcha:1", "captcha:2"]
    return mock


class TestCaptchaManager:
    """验证码管理器测试类"""
    
    async def test_generate_captcha(self, mock_cache_manager):
        """测试生成验证码"""
        # 创建验证码管理器
        captcha_manager = CaptchaManager(mock_cache_manager)
        
        # 生成验证码
        captcha_result = await captcha_manager.generate_captcha(captcha_id="test_id")
        
        # 验证结果
        assert "captcha_id" in captcha_result
        assert "captcha_image" in captcha_result
        assert "expire_in" in captcha_result
        assert captcha_result["captcha_id"] == "test_id"
        assert captcha_result["expire_in"] == 300  # 默认过期时间
        
        # 验证缓存操作
        mock_cache_manager.set.assert_called_once()
        
        # 验证图像格式
        image_data = captcha_result["captcha_image"]
        assert image_data.startswith("data:image/png;base64,")
        
        # 验证Base64解码
        try:
            image_base64 = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))
            assert image.format == "PNG"
        except Exception as e:
            pytest.fail(f"无法解码图像: {str(e)}")
    
    async def test_verify_captcha_success(self, mock_cache_manager):
        """测试验证码验证成功的情况"""
        # 设置模拟响应
        mock_cache_manager.get.return_value = "1234"
        
        # 创建验证码管理器
        captcha_manager = CaptchaManager(mock_cache_manager)
        
        # 验证验证码
        result = await captcha_manager.verify_captcha("test_id", "1234")
        
        # 验证结果
        assert result is True
        
        # 验证缓存操作
        mock_cache_manager.get.assert_called_once_with("captcha:test_id")
        mock_cache_manager.delete.assert_called_once_with("captcha:test_id")
    
    async def test_verify_captcha_case_insensitive(self, mock_cache_manager):
        """测试验证码验证不区分大小写"""
        # 设置模拟响应
        mock_cache_manager.get.return_value = "abcd"
        
        # 创建验证码管理器
        captcha_manager = CaptchaManager(mock_cache_manager)
        
        # 验证验证码 (使用大写)
        result = await captcha_manager.verify_captcha("test_id", "ABCD")
        
        # 验证结果
        assert result is True
        
        # 验证缓存操作
        mock_cache_manager.get.assert_called_once_with("captcha:test_id")
        mock_cache_manager.delete.assert_called_once_with("captcha:test_id")
    
    async def test_verify_captcha_failure_wrong_code(self, mock_cache_manager):
        """测试验证码验证失败 - 错误的验证码"""
        # 设置模拟响应
        mock_cache_manager.get.return_value = "1234"
        
        # 创建验证码管理器
        captcha_manager = CaptchaManager(mock_cache_manager)
        
        # 验证验证码
        result = await captcha_manager.verify_captcha("test_id", "5678")
        
        # 验证结果
        assert result is False
        
        # 验证缓存操作
        mock_cache_manager.get.assert_called_once_with("captcha:test_id")
        mock_cache_manager.delete.assert_called_once_with("captcha:test_id")
    
    async def test_verify_captcha_failure_expired(self, mock_cache_manager):
        """测试验证码验证失败 - 验证码已过期"""
        # 设置模拟响应
        mock_cache_manager.get.return_value = None  # 模拟已过期或不存在
        
        # 创建验证码管理器
        captcha_manager = CaptchaManager(mock_cache_manager)
        
        # 验证验证码
        result = await captcha_manager.verify_captcha("test_id", "1234")
        
        # 验证结果
        assert result is False
        
        # 验证缓存操作
        mock_cache_manager.get.assert_called_once_with("captcha:test_id")
        # 不会调用删除方法，因为验证码已经不存在
        mock_cache_manager.delete.assert_not_called()
    
    async def test_verify_captcha_empty_input(self, mock_cache_manager):
        """测试验证码验证失败 - 输入为空"""
        # 创建验证码管理器
        captcha_manager = CaptchaManager(mock_cache_manager)
        
        # 验证验证码
        result = await captcha_manager.verify_captcha("", "")
        
        # 验证结果
        assert result is False
        
        # 验证缓存操作
        mock_cache_manager.get.assert_not_called()
        mock_cache_manager.delete.assert_not_called()
    
    async def test_clear_expired_captchas(self, mock_cache_manager):
        """测试清理过期验证码"""
        # 设置模拟响应
        mock_cache_manager.keys.return_value = ["captcha:1", "captcha:2", "captcha:3"]
        
        # 创建验证码管理器
        captcha_manager = CaptchaManager(mock_cache_manager)
        
        # 清理过期验证码
        result = await captcha_manager.clear_expired_captchas()
        
        # 验证结果
        assert result == 3  # 应该返回键的数量
        
        # 验证缓存操作
        mock_cache_manager.keys.assert_called_once_with("captcha:*") 