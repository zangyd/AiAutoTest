"""
验证码工具模块
"""
import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional
import base64

class CaptchaGenerator:
    """验证码生成器"""
    
    def __init__(self, 
                 width: int = 160, 
                 height: int = 60, 
                 font_size: int = 35,
                 length: int = 4):
        """
        初始化验证码生成器
        
        Args:
            width: 图片宽度
            height: 图片高度
            font_size: 字体大小
            length: 验证码长度
        """
        self.width = width
        self.height = height
        self.font_size = font_size
        self.length = length
        
    def _generate_text(self) -> str:
        """生成随机验证码文本"""
        # 使用数字和大写字母
        chars = string.digits + string.ascii_uppercase
        # 排除易混淆的字符
        chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
        return ''.join(random.choices(chars, k=self.length))
    
    def _draw_noise(self, draw: ImageDraw, width: int, height: int):
        """绘制干扰线和噪点"""
        # 干扰线
        for _ in range(3):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=(169,169,169))
            
        # 噪点
        for _ in range(30):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.point([x, y], fill=(169,169,169))
            
    def generate(self) -> Tuple[str, str]:
        """
        生成验证码
        
        Returns:
            Tuple[str, str]: (验证码文本, base64编码的图片)
        """
        # 创建画布
        image = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 生成文本
        text = self._generate_text()
        
        try:
            # 尝试加载系统字体
            font = ImageFont.truetype('arial.ttf', self.font_size)
        except:
            # 如果系统字体不可用，使用默认字体
            font = ImageFont.load_default()
        
        # 计算文本大小和位置
        text_width = self.font_size * self.length
        text_x = (self.width - text_width) // 2
        text_y = (self.height - self.font_size) // 2
        
        # 绘制文本
        for i, char in enumerate(text):
            x = text_x + i * self.font_size
            y = text_y + random.randint(-5, 5)  # 随机上下偏移
            draw.text((x, y), char, font=font, fill=(0, 0, 0))
            
        # 添加干扰
        self._draw_noise(draw, self.width, self.height)
        
        # 转换为base64
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return text, f"data:image/png;base64,{image_base64}" 