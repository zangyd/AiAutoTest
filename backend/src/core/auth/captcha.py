"""
验证码生成和验证模块
用于生成图形验证码和验证用户输入的验证码
"""
import io
import random
import string
import time
import logging
import os
import uuid
from io import BytesIO
from typing import Tuple, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import base64
from ..logging.logger import Logger
from core.cache.cache_manager import CacheManager
import threading
from datetime import datetime, timedelta
from redis.exceptions import RedisError

# 配置captcha专用日志记录器
logger = Logger(
    name="captcha",
    log_dir="logs",
    level=logging.INFO,
    console_output=True,
    console_color=True,
    async_mode=False  # 改为同步模式
)

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
    
    def __init__(self, cache_manager: CacheManager, logger: Logger = None):
        """初始化验证码管理器
        
        Args:
            cache_manager: Redis缓存管理器实例，用于存储验证码
            logger: 日志记录器实例，用于记录日志
        """
        self.cache_manager = cache_manager
        self.logger = logger or logging.getLogger(__name__)
        self.key_prefix = "auth:captcha"  # 统一前缀
        self.width = 160
        self.height = 60
        self.font_size = 35
        self.text_length = 4
        self.expire_seconds = 300  # 5分钟过期
        self._setup_font()
        self._lock = threading.Lock()
        
        self.logger.info("验证码管理器初始化完成")
    
    def _setup_font(self):
        """设置字体相关属性"""
        # 字体路径处理
        font_paths = [
            os.path.join(os.path.dirname(__file__), 'fonts', 'default.ttf'),
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/System/Library/Fonts/Monaco.ttf'
        ]
        
        self.font_path = None
        for path in font_paths:
            if os.path.exists(path):
                self.font_path = path
                self.logger.info(f"使用字体: {path}")
                break
        
        if not self.font_path:
            self.logger.warning("无法加载任何TrueType字体，将使用默认字体")
            
    def _get_cache_key(self, captcha_id: str) -> str:
        """生成缓存键
        
        Args:
            captcha_id: 验证码ID
            
        Returns:
            str: 格式化的缓存键
        """
        return f"{self.key_prefix}:{captcha_id}"
    
    def _generate_text(self) -> str:
        """生成随机验证码文本
        
        Returns:
            str: 验证码文本
        """
        chars = string.digits + string.ascii_uppercase
        chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
        return ''.join(random.choice(chars) for _ in range(self.text_length))

    def _generate_colors(self) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """生成随机前景色和背景色
        
        Returns:
            Tuple[Tuple[int, int, int], Tuple[int, int, int]]: (前景色, 背景色)
        """
        fg_color = (random.randint(0, 80), random.randint(0, 80), random.randint(0, 80))
        bg_color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
        return fg_color, bg_color

    def _generate_captcha_image(self, text: str) -> Image.Image:
        """生成验证码图片
        
        Args:
            text: 验证码文本
            
        Returns:
            Image.Image: PIL图片对象
            
        Raises:
            ValueError: 生成图片失败时抛出异常
        """
        try:
            # 创建图片对象
            image = Image.new('RGB', (self.width, self.height), 'white')
            draw = ImageDraw.Draw(image)
            
            # 生成颜色
            fg_color, bg_color = self._generate_colors()
            
            # 填充背景色
            draw.rectangle([(0, 0), (self.width, self.height)], fill=bg_color)
            
            # 加载字体
            try:
                if self.font_path:
                    font = ImageFont.truetype(self.font_path, self.font_size)
                    self.logger.debug(f"使用TrueType字体: {self.font_path}")
                else:
                    font = ImageFont.load_default()
                    self.logger.debug("使用系统默认字体")
            except Exception as e:
                self.logger.warning(f"加载字体失败: {str(e)}，使用默认字体")
                font = ImageFont.load_default()
            
            # 计算每个字符的宽度
            char_width = self.width // (len(text) + 2)  # 留出左右边距
            start_x = char_width  # 起始位置留出一个字符宽度的边距
            
            # 绘制文本
            for i, char in enumerate(text):
                # 计算字符位置
                x = start_x + (i * char_width) + random.randint(-5, 5)  # 添加随机偏移
                y = (self.height - self.font_size) // 2 + random.randint(-5, 5)  # 垂直居中并添加随机偏移
                
                # 确保字符不会超出边界
                x = max(2, min(x, self.width - self.font_size - 2))
                y = max(2, min(y, self.height - self.font_size - 2))
                
                # 随机旋转角度
                angle = random.randint(-30, 30)
                # 创建单个字符的图片
                char_img = Image.new('RGBA', (char_width, self.height), (0, 0, 0, 0))
                char_draw = ImageDraw.Draw(char_img)
                char_draw.text((0, 0), char, font=font, fill=fg_color)
                # 旋转字符
                rotated = char_img.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))
                # 粘贴到主图片
                image.paste(rotated, (x, y), rotated)
            
            # 添加干扰线
            for _ in range(3):
                start_x = random.randint(0, self.width // 4)
                end_x = random.randint(3 * self.width // 4, self.width)
                start_y = random.randint(0, self.height)
                end_y = random.randint(0, self.height)
                draw.line([(start_x, start_y), (end_x, end_y)], 
                         fill=fg_color, 
                         width=random.randint(1, 2))
            
            # 添加噪点
            for _ in range(int(self.width * self.height * 0.05)):  # 5%的噪点密度
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                draw.point((x, y), fill=fg_color)
            
            return image
            
        except Exception as e:
            error_msg = f"生成验证码图片失败: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def _image_to_base64(self, image: Image.Image) -> str:
        """将PIL图片对象转换为base64字符串
        
        Args:
            image: PIL图片对象
            
        Returns:
            str: base64编码的图片数据
        """
        try:
            # 将图片保存到内存中
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            
            # 获取字节数据并进行base64编码
            image_bytes = buffer.getvalue()
            image_base64 = base64.b64encode(image_bytes)
            
            # 如果结果是bytes类型，转换为str
            if isinstance(image_base64, bytes):
                image_base64 = image_base64.decode('utf-8')
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            error_msg = f"图片转base64失败: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def _normalize_text(self, text: str) -> str:
        """规范化验证码文本
        
        Args:
            text: 验证码文本
            
        Returns:
            str: 规范化后的文本
        """
        return str(text).strip().upper()

    def generate_captcha(self) -> Dict[str, str]:
        """生成验证码
        
        Returns:
            Dict[str, str]: 包含验证码ID和图片base64数据的字典
        """
        start_time = time.time()
        try:
            with self._lock:
                # 生成验证码文本
                text = self._generate_text()
                self.logger.info("开始生成验证码")
                
                # 创建图片对象并生成验证码
                image = self._generate_captcha_image(text)
                
                # 使用_image_to_base64方法转换图片
                image_base64_data = self._image_to_base64(image)
                
                # 生成验证码ID并存储
                captcha_id = str(uuid.uuid4())
                cache_key = self._get_cache_key(captcha_id)
                
                # 存储规范化的验证码文本
                normalized_text = self._normalize_text(text)
                if not self.cache_manager.set_sync(cache_key, normalized_text, self.expire_seconds):
                    self.logger.error(f"存储验证码失败: ID={captcha_id}, 文本={normalized_text}")
                    raise ValueError("存储验证码失败")
                
                end_time = time.time()
                generation_time = round((end_time - start_time) * 1000, 2)
                
                self.logger.info(f"验证码生成成功 - ID: {captcha_id}, 文本: {normalized_text}, 过期时间: {self.expire_seconds}秒, 耗时: {generation_time}ms")
                self.logger.debug(f"验证码详情 - 缓存键: {cache_key}, 文本长度: {len(normalized_text)}")
                
                return {
                    'captcha_id': captcha_id,
                    'captcha_image': image_base64_data,
                    'expire_in': self.expire_seconds
                }
                
        except Exception as e:
            error_msg = f"生成验证码失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)

    def verify_captcha_sync(self, captcha_id: str, captcha_text: str) -> bool:
        """同步验证验证码
        
        Args:
            captcha_id: 验证码ID
            captcha_text: 用户输入的验证码文本
            
        Returns:
            bool: 验证是否成功
        """
        start_time = time.time()
        
        try:
            with self._lock:
                # 参数验证
                if not captcha_id or not captcha_text:
                    self.logger.warning(f"验证码参数无效 - ID: {captcha_id}, 文本: {captcha_text}")
                    return False
                
                # 获取缓存的验证码
                cache_key = self._get_cache_key(captcha_id)
                self.logger.info(f"开始验证 - 缓存键: {cache_key}")
                
                # 获取存储的验证码
                stored_text = self.cache_manager.get_sync(cache_key)
                if not stored_text:
                    self.logger.warning(f"验证码不存在或已过期 - ID: {captcha_id}, 缓存键: {cache_key}")
                    return False
                
                # 规范化验证码文本
                input_text = self._normalize_text(captcha_text)
                stored_text = self._normalize_text(stored_text)
                
                # 记录验证详情
                self.logger.info(f"验证码比对 - ID: {captcha_id}")
                self.logger.debug(f"存储的验证码: [{stored_text}], 输入的验证码: [{input_text}]")
                
                # 比较验证码
                result = stored_text == input_text
                
                # 验证后立即删除验证码
                if result:
                    try:
                        if self.cache_manager.delete_sync(cache_key):
                            self.logger.info(f"验证码已删除 - 缓存键: {cache_key}")
                        else:
                            self.logger.warning(f"验证码删除失败 - 缓存键: {cache_key}")
                    except Exception as e:
                        self.logger.error(f"删除验证码时发生错误: {str(e)}")
                
                end_time = time.time()
                verification_time = round((end_time - start_time) * 1000, 2)
                
                if result:
                    self.logger.info(f"验证码验证成功 - ID: {captcha_id}, 耗时: {verification_time}ms")
                else:
                    self.logger.warning(
                        f"验证码验证失败 - ID: {captcha_id}, "
                        f"存储值: [{stored_text}]({len(stored_text)}), "
                        f"输入值: [{input_text}]({len(input_text)}), "
                        f"耗时: {verification_time}ms"
                    )
                
                return result
                
        except Exception as e:
            self.logger.error(f"验证码验证异常 - ID: {captcha_id}, 文本: {captcha_text}, 错误: {str(e)}", exc_info=True)
            return False

    def verify_captcha(self, captcha_id: str, captcha_text: str) -> bool:
        """验证验证码
        
        Args:
            captcha_id: 验证码ID
            captcha_text: 用户输入的验证码文本
            
        Returns:
            bool: 验证是否通过
        """
        return self.verify_captcha_sync(captcha_id, captcha_text)

    def clear_expired_captchas(self) -> None:
        """清理过期的验证码
        
        此方法会扫描所有验证码缓存键，检查其TTL并删除已过期的验证码。
        建议在后台任务中定期调用此方法以清理过期数据。
        
        Returns:
            None
        """
        try:
            # 构建验证码键的模式
            pattern = f"{self.key_prefix}:*"
            
            # 获取所有匹配的键
            keys = self.cache_manager.redis.keys(pattern)
            
            if not keys:
                self.logger.info("没有找到需要清理的验证码")
                return
                
            # 检查每个键的TTL
            expired_keys = []
            for key in keys:
                ttl = self.cache_manager.ttl_sync(key)
                # ttl <= 0 表示键已过期或不存在
                if ttl <= 0:
                    expired_keys.append(key)
            
            # 如果有过期的键，则删除它们
            if expired_keys:
                deleted = self.cache_manager.redis.delete(*expired_keys)
                self.logger.info(f"成功清理 {deleted} 个过期验证码")
            else:
                self.logger.info("没有过期的验证码需要清理")
                
        except Exception as e:
            self.logger.error(f"清理过期验证码时发生错误: {str(e)}") 