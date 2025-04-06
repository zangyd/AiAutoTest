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
        form_data: OAuth2PasswordRequestForm,
        remember: bool = False
    ) -> Tuple[UserOut, TokenResponse]:
        """
        用户认证
        
        Args:
            form_data: OAuth2表单数据
            remember: 是否记住登录状态
            
        Returns:
            Tuple[UserOut, TokenResponse]: 用户信息和令牌信息
            
        Raises:
            HTTPException: 认证失败时抛出异常
        """
        # 模拟用户认证
        if form_data.username == "test_user" and form_data.password == "password":
            user = UserOut(
                id=1,
                username="test_user",
                email="test@example.com",
                is_active=True,
                is_superuser=False
            )
            
            # 创建访问令牌和刷新令牌
            access_token = create_access_token({"sub": str(user.id)})
            refresh_token = create_refresh_token({"sub": str(user.id)})
            
            token = TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=3600,
                refresh_token=refresh_token
            )
            
            return user, token
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"}
            )

# 创建认证服务实例
auth_service = AuthService() 