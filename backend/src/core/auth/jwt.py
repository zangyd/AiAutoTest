from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from fastapi import HTTPException, status
from redis import Redis

from ..config.jwt_config import jwt_settings


class JWTHandler:
    """JWT处理器"""

    def __init__(self, redis_client: Optional[Redis] = None):
        """
        初始化JWT处理器
        
        Args:
            redis_client: Redis客户端实例，用于管理令牌黑名单
        """
        self.redis_client = redis_client

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        创建访问令牌
        
        Args:
            data: 要编码到令牌中的数据
            
        Returns:
            str: JWT令牌字符串
        """
        to_encode = data.copy()
        # 设置过期时间
        expire = datetime.utcnow() + jwt_settings.access_token_expires
        to_encode.update({"exp": expire})
        # 编码JWT
        encoded_jwt = jwt.encode(
            to_encode,
            jwt_settings.SECRET_KEY,
            algorithm=jwt_settings.ALGORITHM
        )
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        创建刷新令牌
        
        Args:
            data: 要编码到令牌中的数据
            
        Returns:
            str: JWT刷新令牌字符串
        """
        to_encode = data.copy()
        # 设置过期时间
        expire = datetime.utcnow() + jwt_settings.refresh_token_expires
        to_encode.update({"exp": expire, "refresh": True})
        # 编码JWT
        encoded_jwt = jwt.encode(
            to_encode,
            jwt_settings.SECRET_KEY,
            algorithm=jwt_settings.ALGORITHM
        )
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌字符串
            
        Returns:
            Dict[str, Any]: 解码后的令牌数据
            
        Raises:
            HTTPException: 当令牌无效或已过期时
        """
        try:
            # 检查令牌是否在黑名单中
            if self.redis_client and self.redis_client.get(f"blacklist:{token}"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 解码并验证令牌
            payload = jwt.decode(
                token,
                jwt_settings.SECRET_KEY,
                algorithms=[jwt_settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def revoke_token(self, token: str) -> None:
        """
        将令牌加入黑名单
        
        Args:
            token: 要加入黑名单的令牌
        """
        if self.redis_client:
            # 解码令牌以获取过期时间
            try:
                payload = jwt.decode(
                    token,
                    jwt_settings.SECRET_KEY,
                    algorithms=[jwt_settings.ALGORITHM]
                )
                exp = datetime.fromtimestamp(payload["exp"])
                ttl = (exp - datetime.utcnow()).total_seconds()
                
                # 将令牌加入黑名单，过期时间与令牌相同
                if ttl > 0:
                    self.redis_client.setex(
                        f"blacklist:{token}",
                        int(ttl),
                        "revoked"
                    )
            except (jwt.ExpiredSignatureError, jwt.JWTError):
                # 如果令牌已过期或无效，则不需要加入黑名单
                pass


# 创建JWT处理器实例
jwt_handler = JWTHandler() 