"""
认证服务
"""
from typing import Tuple, Optional
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .schemas import TokenResponse, UserOut
from .jwt import create_access_token, create_refresh_token

class AuthService:
    """认证服务类"""
    
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
        # 模拟用户认证
        if username == "test_user" and password == "password":
            return UserOut(
                id=1,
                username="test_user",
                email="test@example.com",
                is_active=True,
                is_superuser=False
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"}
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
        # 创建访问令牌和刷新令牌
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600 if not remember else 7 * 24 * 3600,
            refresh_token=refresh_token
        )

# 创建认证服务实例
auth_service = AuthService() 