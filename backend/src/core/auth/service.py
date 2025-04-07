"""
认证服务
"""
from typing import Tuple, Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from api.services.user import UserService
from core.security import create_access_token, create_refresh_token
from .schemas import TokenResponse, UserOut

class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.user_service = UserService(db)
    
    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> UserOut:
        """
        用户认证
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            UserOut: 用户信息
            
        Raises:
            HTTPException: 认证失败时抛出异常
        """
        # 从数据库获取用户
        user = self.user_service.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 验证密码
        if not self.user_service.verify_password(user, password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户未激活"
            )
        
        return UserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_superuser=user.is_superuser
        )
            
    async def create_access_token(
        self,
        user: UserOut,
        remember: bool = False
    ) -> TokenResponse:
        """
        创建访问令牌
        
        Args:
            user: 用户信息
            remember: 是否记住登录状态
            
        Returns:
            TokenResponse: 令牌信息
        """
        # 获取用户权限
        user_db = self.user_service.get_user_by_id(user.id)
        permissions = self.user_service.get_user_permissions(user_db)
        
        # 创建令牌数据
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "permissions": list(permissions)
        }
        
        # 创建访问令牌和刷新令牌
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600 if not remember else 7 * 24 * 3600,
            refresh_token=refresh_token
        )

# 创建认证服务实例
auth_service = AuthService() 