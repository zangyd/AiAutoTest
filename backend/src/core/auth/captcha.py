"""
验证码生成和验证模块
用于生成图形验证码和验证用户输入的验证码
"""
import io
import random
import string
import time
from typing import Tuple, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import base64

# 默认字体大小
DEFAULT_FONT_SIZE = 38
# 默认字体 - 这里假设系统中有这个字体，实际部署时需要确保
DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# 验证码过期时间（秒）
CAPTCHA_EXPIRE_SECONDS = 300
# 默认验证码长度
DEFAULT_CAPTCHA_LENGTH = 4
# 默认图片尺寸
DEFAULT_IMAGE_SIZE = (120, 50)
# 背景色范围
BACKGROUND_COLOR_RANGE = (230, 255)
# 文字颜色范围
TEXT_COLOR_RANGE = (0, 100)


class CaptchaManager:
    """验证码管理器，负责生成和验证验证码"""
    
    def __init__(self, cache_manager):
        """初始化验证码管理器
        
        Args:
            cache_manager: Redis缓存管理器实例，用于存储验证码
        """
        self.cache_manager = cache_manager
        self.key_prefix = "captcha"
    
    def _get_cache_key(self, captcha_id: str) -> str:
        """生成缓存键名
        
        Args:
            captcha_id: 验证码ID
            
        Returns:
            str: 缓存键名
        """
        return f"{self.key_prefix}:{captcha_id}"
    
    async def generate_captcha(self, captcha_id: str = None, length: int = DEFAULT_CAPTCHA_LENGTH) -> Dict:
        """生成验证码
        
        Args:
            captcha_id: 验证码ID，如果不提供则自动生成
            length: 验证码长度
            
        Returns:
            Dict: 包含验证码图片和ID的字典
        """
        # 如果未提供ID，生成一个随机ID
        if not captcha_id:
            captcha_id = f"captcha_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # 生成随机验证码文本
        captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        
        # 创建图像对象
        image = self._generate_captcha_image(captcha_text)
        
        # 将图片转换为base64编码
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # 存储验证码到缓存
        await self.cache_manager.set(
            self._get_cache_key(captcha_id),
            captcha_text.lower(),  # 存储小写以便验证时不区分大小写
            ttl=CAPTCHA_EXPIRE_SECONDS
        )
        
        return {
            "captcha_id": captcha_id,
            "captcha_image": f"data:image/png;base64,{img_str}",
            "expire_in": CAPTCHA_EXPIRE_SECONDS
        }
    
    def _generate_captcha_image(self, text: str) -> Image.Image:
        """生成验证码图片
        
        Args:
            text: 验证码文本
            
        Returns:
            Image.Image: PIL图像对象
        """
        # 创建图像对象
        width, height = DEFAULT_IMAGE_SIZE
        image = Image.new('RGB', (width, height), color=self._random_light_color())
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            font = ImageFont.truetype(DEFAULT_FONT_PATH, DEFAULT_FONT_SIZE)
        except IOError:
            font = ImageFont.load_default()
        
        # 计算文本位置使其居中
        text_width = font.getsize(text)[0]
        text_height = font.getsize(text)[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # 绘制文字
        for i, char in enumerate(text):
            # 每个字符使用不同颜色
            color = self._random_dark_color()
            # 每个字符有轻微偏移以增加复杂度
            offset_x = random.randint(-2, 2)
            offset_y = random.randint(-2, 2)
            draw.text((x + i * (text_width // len(text)) + offset_x, y + offset_y), char, font=font, fill=color)
        
        # 添加干扰点
        self._add_noise_dots(draw, width, height)
        
        # 添加干扰线
        self._add_noise_lines(draw, width, height)
        
        return image
    
    def _random_light_color(self) -> Tuple[int, int, int]:
        """生成随机浅色
        
        Returns:
            Tuple[int, int, int]: RGB颜色元组
        """
        return (
            random.randint(BACKGROUND_COLOR_RANGE[0], BACKGROUND_COLOR_RANGE[1]),
            random.randint(BACKGROUND_COLOR_RANGE[0], BACKGROUND_COLOR_RANGE[1]),
            random.randint(BACKGROUND_COLOR_RANGE[0], BACKGROUND_COLOR_RANGE[1])
        )
    
    def _random_dark_color(self) -> Tuple[int, int, int]:
        """生成随机深色
        
        Returns:
            Tuple[int, int, int]: RGB颜色元组
        """
        return (
            random.randint(TEXT_COLOR_RANGE[0], TEXT_COLOR_RANGE[1]),
            random.randint(TEXT_COLOR_RANGE[0], TEXT_COLOR_RANGE[1]),
            random.randint(TEXT_COLOR_RANGE[0], TEXT_COLOR_RANGE[1])
        )
    
    def _add_noise_dots(self, draw: ImageDraw.Draw, width: int, height: int, count: int = 50) -> None:
        """添加干扰点
        
        Args:
            draw: ImageDraw对象
            width: 图片宽度
            height: 图片高度
            count: 干扰点数量
        """
        for _ in range(count):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.point((x, y), fill=self._random_dark_color())
    
    def _add_noise_lines(self, draw: ImageDraw.Draw, width: int, height: int, count: int = 3) -> None:
        """添加干扰线
        
        Args:
            draw: ImageDraw对象
            width: 图片宽度
            height: 图片高度
            count: 干扰线数量
        """
        for _ in range(count):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line((x1, y1, x2, y2), fill=self._random_dark_color())
    
    async def verify_captcha(self, captcha_id: str, captcha_text: str) -> bool:
        """验证验证码
        
        Args:
            captcha_id: 验证码ID
            captcha_text: 用户输入的验证码
            
        Returns:
            bool: 验证是否成功
        """
        if not captcha_id or not captcha_text:
            return False
        
        # 从缓存中获取验证码
        cached_text = await self.cache_manager.get(self._get_cache_key(captcha_id))
        
        # 如果验证码不存在或已过期
        if not cached_text:
            return False
        
        # 验证码比较（不区分大小写）
        is_valid = cached_text.lower() == captcha_text.lower()
        
        # 验证后，无论成功与否都删除验证码（一次性使用）
        await self.cache_manager.delete(self._get_cache_key(captcha_id))
        
        return is_valid
    
    async def clear_expired_captchas(self) -> int:
        """清理过期的验证码
        注意：在使用Redis时这通常不需要，因为Redis会自动过期键。
        但在某些情况下可能需要手动清理。
        
        Returns:
            int: 清理的验证码数量
        """
        # 查找所有验证码键
        pattern = f"{self.key_prefix}:*"
        keys = await self.cache_manager.keys(pattern)
        
        # Redis会自动过期键，所以这里不需要额外的清理逻辑
        # 但我们可以返回当前的验证码数量作为参考
        return len(keys) 