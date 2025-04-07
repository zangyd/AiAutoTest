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
from core.auth.token_blacklist import TokenBlacklist
from core.auth.captcha import CaptchaManager
from core.auth.login_log import LoginLogService

class AuthService:
    """认证服务类"""
    
    def __init__(
        self, 
        db: Session = Depends(get_db), 
        redis: Redis = Depends(get_redis),
        token_blacklist: TokenBlacklist = None,
        captcha_manager: CaptchaManager = None
    ):
        """
        初始化认证服务
        
        Args:
            db: 数据库会话
            redis: Redis客户端
            token_blacklist: 令牌黑名单服务
            captcha_manager: 验证码管理器
        """
        self.db = db
        self.redis = redis
        self.user_service = UserService(db)
        self.token_blacklist = token_blacklist
        self.captcha_manager = captcha_manager
    
    async def authenticate_user(
        self, 
        username: str, 
        password: str, 
        captcha_id: Optional[str] = None, 
        captcha_text: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> User:
        """
        验证用户凭据并返回用户对象

        Args:
            username: 用户名
            password: 密码
            captcha_id: 验证码ID（可选）
            captcha_text: 验证码文本（可选）
            ip_address: 用户IP地址（可选，用于日志记录）
            user_agent: 用户代理信息（可选，用于日志记录）

        Returns:
            User: 用户对象

        Raises:
            InvalidCredentialsException: 如果凭据无效
            InactiveUserException: 如果用户被禁用
            CaptchaVerificationFailedException: 如果验证码验证失败
        """
        # 验证码校验
        captcha_verified = False
        if self.captcha_manager and captcha_id and captcha_text:
            captcha_verified = await self.captcha_manager.verify_captcha(captcha_id, captcha_text)
            if not captcha_verified:
                # 记录登录失败日志
                await LoginLogService.add_login_log(
                    db=self.db,
                    username=username,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    login_status=False,
                    status_message="验证码验证失败",
                    captcha_verified=False
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="验证码验证失败"
                )

        # 查找用户
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            # 记录登录失败日志
            await LoginLogService.add_login_log(
                db=self.db,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                login_status=False,
                status_message="用户名或密码错误",
                captcha_verified=captcha_verified
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        if not user.is_active:
            # 记录登录失败日志
            await LoginLogService.add_login_log(
                db=self.db,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                login_status=False,
                status_message="用户已禁用",
                captcha_verified=captcha_verified
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已禁用"
            )

        # 记录登录成功日志
        await LoginLogService.add_login_log(
            db=self.db,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            login_status=True,
            status_message="登录成功",
            captcha_verified=captcha_verified
        )

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

    async def generate_captcha(self) -> Dict:
        """
        生成验证码

        Returns:
            Dict: 包含验证码信息的字典
        """
        if not self.captcha_manager:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="验证码服务未配置"
            )
        
        return await self.captcha_manager.generate_captcha()

# 创建认证服务实例
auth_service = AuthService() 