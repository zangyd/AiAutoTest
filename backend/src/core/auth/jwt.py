"""
JWT处理模块
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException

from ..config.jwt_config import jwt_settings


class JWTHandler:
    """JWT处理类"""
    
    def __init__(self, redis_client=None):
        """
        初始化JWT处理器
        
        Args:
            redis_client: Redis客户端实例，用于令牌黑名单
        """
        self.secret_key = jwt_settings.SECRET_KEY
        self.algorithm = jwt_settings.ALGORITHM
        self.access_token_expire_minutes = jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = jwt_settings.REFRESH_TOKEN_EXPIRE_DAYS
        self.redis_client = redis_client
    
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
            HTTPException: 当令牌无效时
        """
        try:
            # 检查令牌是否被撤销
            if self.redis_client and self.redis_client.get(f"blacklist:{token}"):
                raise HTTPException(
                    status_code=401,
                    detail="Token has been revoked"
                )
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials"
            )
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        创建访问令牌
        
        Args:
            data: 要编码的数据
            
        Returns:
            str: 访问令牌
        """
        return self.create_token(data)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        创建刷新令牌
        
        Args:
            data: 要编码的数据
            
        Returns:
            str: 刷新令牌
        """
        data = data.copy()
        data["refresh"] = True
        expires_delta = timedelta(days=self.refresh_token_expire_days)
        return self.create_token(data, expires_delta)
    
    def revoke_token(self, token: str) -> None:
        """
        将令牌加入黑名单
        
        Args:
            token: 要撤销的令牌
        """
        if not self.redis_client:
            raise RuntimeError("Redis client is required for token revocation")
            
        # 解码令牌以获取过期时间
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        exp = datetime.fromtimestamp(payload["exp"])
        ttl = int((exp - datetime.utcnow()).total_seconds())
        
        if ttl > 0:
            self.redis_client.setex(f"blacklist:{token}", ttl, "revoked")


# 创建全局JWT处理器实例
jwt_handler = JWTHandler() 