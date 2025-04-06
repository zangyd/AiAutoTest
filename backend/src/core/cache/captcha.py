"""
验证码缓存服务
"""
from datetime import datetime, timedelta
from typing import Optional
import redis
from ..config import settings

class CaptchaCache:
    """验证码缓存服务"""
    
    def __init__(self):
        """初始化Redis连接"""
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self.expire_time = 300  # 验证码有效期5分钟
        
    def _get_key(self, captcha_id: str) -> str:
        """生成Redis键名"""
        return f"captcha:{captcha_id}"
        
    def save_captcha(self, captcha_id: str, code: str) -> bool:
        """
        保存验证码
        
        Args:
            captcha_id: 验证码ID
            code: 验证码内容
            
        Returns:
            bool: 是否保存成功
        """
        key = self._get_key(captcha_id)
        try:
            self.redis.setex(key, self.expire_time, code.upper())
            return True
        except:
            return False
            
    def verify_captcha(self, captcha_id: str, code: str) -> bool:
        """
        验证验证码
        
        Args:
            captcha_id: 验证码ID
            code: 用户输入的验证码
            
        Returns:
            bool: 验证是否通过
        """
        key = self._get_key(captcha_id)
        try:
            stored_code = self.redis.get(key)
            if not stored_code:
                return False
            
            # 验证成功后删除验证码
            self.redis.delete(key)
            
            return stored_code == code.upper()
        except:
            return False
            
    def get_captcha(self, captcha_id: str) -> Optional[str]:
        """
        获取验证码
        
        Args:
            captcha_id: 验证码ID
            
        Returns:
            Optional[str]: 验证码内容，如果不存在则返回None
        """
        key = self._get_key(captcha_id)
        try:
            return self.redis.get(key)
        except:
            return None 