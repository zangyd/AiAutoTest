"""
认证服务层，实现认证相关的业务逻辑
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from core.auth.jwt import create_access_token, create_refresh_token
from core.auth.schemas import TokenResponse
from core.database import get_session
from core.redis import get_redis
from core.security import verify_password, get_password_hash
from models.user import User
from .constants import AuthErrorCode

class AuthService:
    """认证服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.db: AsyncSession = get_session()
        self.redis = get_redis()
        
    async def verify_login(
        self,
        username: str,
        password: str,
        captcha_id: str,
        captcha_code: str,
        remember: bool = False
    ) -> TokenResponse:
        """
        验证登录信息
        
        Args:
            username: 用户名
            password: 密码
            captcha_id: 验证码ID
            captcha_code: 验证码
            remember: 是否记住登录状态
            
        Returns:
            TokenResponse: 令牌信息
            
        Raises:
            HTTPException: 登录验证失败时抛出异常
        """
        # 验证验证码
        if not await self._verify_captcha(captcha_id, captcha_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": AuthErrorCode.INVALID_CAPTCHA.code,
                    "message": AuthErrorCode.INVALID_CAPTCHA.message
                }
            )
            
        # 检查用户是否被锁定
        if await self._is_user_locked(username):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": AuthErrorCode.ACCOUNT_LOCKED.code,
                    "message": AuthErrorCode.ACCOUNT_LOCKED.message
                }
            )
            
        # 验证用户名和密码
        user = await self._verify_credentials(username, password)
        if not user:
            await self._increment_failed_attempts(username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": AuthErrorCode.INVALID_CREDENTIALS.code,
                    "message": AuthErrorCode.INVALID_CREDENTIALS.message
                }
            )
            
        # 清除失败次数
        await self._clear_failed_attempts(username)
        
        # 生成令牌
        access_token = await create_access_token(user.id)
        refresh_token = await create_refresh_token(user.id) if remember else None
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
    async def logout(self, user_id: int) -> None:
        """
        用户登出
        
        Args:
            user_id: 用户ID
        """
        # 将当前token加入黑名单
        token = await self._get_current_token()
        if token:
            await self.redis.setex(
                f"blacklist:{token}",
                timedelta(days=1),
                "1"
            )
            
    async def reset_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> None:
        """
        重置密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Raises:
            HTTPException: 密码重置失败时抛出异常
        """
        # 验证旧密码
        user = await self.db.get(User, user_id)
        if not user or not verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": AuthErrorCode.INVALID_PASSWORD.code,
                    "message": AuthErrorCode.INVALID_PASSWORD.message
                }
            )
            
        # 更新密码
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        await self.db.commit()
        
        # 清除所有token
        await self._revoke_all_tokens(user_id)
        
    async def _verify_captcha(self, captcha_id: str, captcha_code: str) -> bool:
        """验证验证码"""
        stored_code = await self.redis.get(f"captcha:{captcha_id}")
        if not stored_code or stored_code.decode() != captcha_code.upper():
            return False
        await self.redis.delete(f"captcha:{captcha_id}")
        return True
        
    async def _verify_credentials(self, username: str, password: str) -> Optional[User]:
        """验证用户凭证"""
        user = await self.db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
        
    async def _is_user_locked(self, username: str) -> bool:
        """检查用户是否被锁定"""
        key = f"login:failed:{username}"
        attempts = await self.redis.get(key)
        if not attempts:
            return False
        return int(attempts) >= 5  # 最大失败次数
        
    async def _increment_failed_attempts(self, username: str) -> None:
        """增加登录失败次数"""
        key = f"login:failed:{username}"
        await self.redis.incr(key)
        await self.redis.expire(key, 1800)  # 30分钟后过期
        
    async def _clear_failed_attempts(self, username: str) -> None:
        """清除登录失败次数"""
        key = f"login:failed:{username}"
        await self.redis.delete(key)
        
    async def _get_current_token(self) -> Optional[str]:
        """获取当前token"""
        # 从请求头中获取token的实现
        pass
        
    async def _revoke_all_tokens(self, user_id: int) -> None:
        """撤销用户所有token"""
        # 将用户的token版本号+1，使所有旧token失效
        user = await self.db.get(User, user_id)
        if user:
            user.token_version = (user.token_version or 0) + 1
            await self.db.commit() 