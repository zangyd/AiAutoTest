"""
认证服务
"""
from typing import Dict, Any, Tuple, Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from redis.asyncio import Redis
import jwt
from datetime import datetime

from core.config import settings
from core.database import get_db
from core.database.redis import get_redis
from api.services.user import UserService
from core.security import create_access_token, create_refresh_token
from .schemas import TokenResponse, UserOut
from .jwt import verify_token, revoke_token
from .models import User
from .utils import verify_password

class AuthService:
    """认证服务类"""
    
    def __init__(
        self, 
        db: Session = Depends(get_db), 
        redis: Redis = Depends(get_redis)
    ):
        """
        初始化认证服务
        
        Args:
            db: 数据库会话
            redis: Redis客户端
        """
        self.db = db
        self.redis = redis
        self.user_service = UserService(db)
    
    async def authenticate_user(self, username: str, password: str) -> User:
        """
        验证用户凭据
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            User: 已验证的用户对象
            
        Raises:
            HTTPException: 认证失败时抛出异常
        """
        # 查询用户
        user = self.user_service.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码不正确",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 验证密码
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码不正确",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    async def create_tokens(self, user: User) -> Tuple[str, str]:
        """
        为用户创建访问令牌和刷新令牌
        
        Args:
            user: 用户对象
            
        Returns:
            Tuple[str, str]: 访问令牌和刷新令牌
        """
        # 准备令牌数据
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
        }
        
        # 创建访问令牌和刷新令牌
        access_token = await create_access_token(token_data)
        refresh_token = await create_refresh_token(token_data)
        
        return access_token, refresh_token
    
    async def refresh_access_token(self, refresh_token: str) -> str:
        """
        使用刷新令牌获取新的访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            str: 新的访问令牌
            
        Raises:
            HTTPException: 刷新令牌无效或不是刷新令牌
        """
        try:
            # 验证刷新令牌
            payload = await verify_token(refresh_token, self.redis)
            
            # 检查是否是刷新令牌
            if not payload.get("refresh"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的刷新令牌",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 获取用户ID
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的令牌内容",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 查询用户信息
            user = self.user_service.get_user_by_id(int(user_id))
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在或已禁用",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 创建新的访问令牌
            token_data = {
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
            }
            
            return await create_access_token(token_data)
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="刷新令牌已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (jwt.InvalidTokenError, jwt.DecodeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def logout(self, token: str) -> bool:
        """
        用户登出，将令牌加入黑名单
        
        Args:
            token: JWT令牌
            
        Returns:
            bool: 是否成功登出
        """
        return await revoke_token(token, self.redis)
    
    async def get_current_user_from_token(self, token: str) -> User:
        """
        从令牌中获取当前用户
        
        Args:
            token: JWT令牌
            
        Returns:
            User: 当前用户对象
            
        Raises:
            HTTPException: 令牌无效或用户不存在
        """
        # 验证令牌
        payload = await verify_token(token, self.redis)
        
        # 获取用户ID
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌内容",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 查询用户
        user = self.user_service.get_user_by_id(int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user

# 创建认证服务实例
auth_service = AuthService() 