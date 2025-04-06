"""
JWT处理模块
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt

from ..config.jwt_config import jwt_settings


class JWTHandler:
    """JWT处理类"""
    
    def __init__(self):
        """初始化JWT处理器"""
        self.secret_key = jwt_settings.SECRET_KEY
        self.algorithm = jwt_settings.ALGORITHM
        self.access_token_expire_minutes = jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = jwt_settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建JWT令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            str: JWT令牌
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            Dict[str, Any]: 解码后的数据
            
        Raises:
            JWTError: 当令牌无效时
        """
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        创建刷新令牌
        
        Args:
            data: 要编码的数据
            
        Returns:
            str: 刷新令牌
        """
        expires_delta = timedelta(days=self.refresh_token_expire_days)
        return self.create_token(data, expires_delta)


# 创建全局JWT处理器实例
jwt_handler = JWTHandler() 