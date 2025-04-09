"""
认证服务模块
"""
from typing import Dict, Any, Optional, Union, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
import logging
import os
import redis
from jose import JWTError
from passlib.context import CryptContext
from core.utils.singleton import Singleton
from core.config.settings import settings
from core.config.jwt_config import jwt_settings
from core.database import get_db
from core.security import verify_password, pwd_context, get_password_hash
from .models import User, LoginLog
from .schemas import TokenData, TokenResponse
from core.logging import logger
from .captcha import CaptchaManager
from api.services.user import UserService
from core.cache import CacheManager
from core.database.session import Base, metadata, SessionLocal
from core.redis import get_redis
from core.exceptions import InvalidCredentialsException, TokenBlacklistedException
from core.security import create_tokens, verify_token

# 配置auth专用日志记录器
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs")
auth_logger = logger

def check_redis_alive(redis_client: redis.Redis) -> bool:
    """检查Redis连接是否有效
    
    Args:
        redis_client: Redis客户端实例
        
    Returns:
        bool: 连接有效返回True，否则返回False
    """
    try:
        redis_client.ping()
        return True
    except redis.RedisError:
        return False

class RedisClient(metaclass=Singleton):
    """Redis客户端单例类"""
    
    def __init__(self):
        """初始化Redis客户端"""
        self._client = None
        self._connect()
    
    def _connect(self) -> None:
        """创建Redis连接"""
        try:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # 测试连接
            self._client.ping()
            auth_logger.info(f"Redis连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except redis.ConnectionError as e:
            auth_logger.error(f"Redis连接失败: {str(e)}")
            raise
    
    def get_client(self) -> redis.Redis:
        """获取Redis客户端实例"""
        if not self._client or not check_redis_alive(self._client):
            self._connect()
        return self._client

class AuthService(metaclass=Singleton):
    """认证服务类"""
    
    def __init__(self):
        """初始化认证服务"""
        self._redis = get_redis()
        self._db = next(get_db())
        self._pwd_context = pwd_context
        self._token_blacklist_key = "token_blacklist"
        self._max_login_attempts = settings.MAX_LOGIN_ATTEMPTS
        self._lockout_duration = settings.ACCOUNT_LOCKOUT_MINUTES
        
        # 初始化数据库会话
        self.db = SessionLocal()
        
        # 初始化用户服务
        self.user_service = UserService(self.db)
        
        # 初始化缓存管理器
        self._cache_manager = CacheManager(self._redis)
        
        # 初始化验证码管理器
        self.captcha_manager = CaptchaManager(
            cache_manager=self._cache_manager,
            logger=auth_logger
        )
        
        auth_logger.info("认证服务初始化完成")
    
    def __del__(self):
        """析构函数，确保关闭数据库连接"""
        if hasattr(self, 'db'):
            self.db.close()
    
    @property
    def redis(self) -> redis.Redis:
        """获取Redis客户端"""
        return self._redis
    
    def add_token_to_blacklist(self, token: str) -> None:
        """将token加入黑名单"""
        try:
            self.redis.setex(
                f"{self._token_blacklist_key}:{token}",
                jwt_settings.BLACKLIST_TOKEN_EXPIRES,
                "1"
            )
            auth_logger.info(f"Token已加入黑名单，将在{jwt_settings.BLACKLIST_TOKEN_EXPIRES}秒后过期")
        except redis.RedisError as e:
            auth_logger.error(f"将token加入黑名单时发生错误: {str(e)}")
            raise
    
    def is_token_blacklisted(self, token: str) -> bool:
        """检查token是否在黑名单中"""
        try:
            return bool(self.redis.exists(f"{self._token_blacklist_key}:{token}"))
        except redis.RedisError as e:
            auth_logger.error(f"检查token黑名单状态时发生错误: {str(e)}")
            return True  # 安全起见，发生错误时返回True
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return verify_password(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希值"""
        return get_password_hash(password)
    
    def create_tokens(self, user: User) -> TokenResponse:
        """创建访问令牌和刷新令牌"""
        try:
            # 基本的令牌数据
            token_data = {
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "is_superuser": user.is_superuser,
                "iss": jwt_settings.JWT_ISSUER,
                "aud": jwt_settings.JWT_AUDIENCE
            }
            
            # 生成访问令牌
            access_token_data = {
                **token_data,
                "exp": datetime.utcnow() + jwt_settings.access_token_expires,
                "type": "access"
            }
            
            access_token = jwt.encode(
                access_token_data,
                jwt_settings.JWT_SECRET_KEY,
                algorithm=jwt_settings.JWT_ALGORITHM
            )
            
            # 生成刷新令牌
            refresh_token_data = {
                "sub": str(user.id),
                "exp": datetime.utcnow() + jwt_settings.refresh_token_expires,
                "type": "refresh"
            }
            
            refresh_token = jwt.encode(
                refresh_token_data,
                jwt_settings.JWT_SECRET_KEY,
                algorithm=jwt_settings.JWT_ALGORITHM
            )
            
            # 存储刷新令牌
            self.redis.setex(
                f"refresh_token:{user.id}",
                int(jwt_settings.refresh_token_expires.total_seconds()),
                refresh_token
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=jwt_settings.JWT_TOKEN_TYPE,
                expires_in=int(jwt_settings.access_token_expires.total_seconds())
            )
            
        except Exception as e:
            auth_logger.error(f"创建令牌失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="令牌创建失败"
            )
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        """验证令牌"""
        try:
            if self.is_token_blacklisted(token):
                return None
                
            payload = jwt.decode(
                token,
                jwt_settings.JWT_SECRET_KEY,
                algorithms=[jwt_settings.JWT_ALGORITHM],
                audience=jwt_settings.JWT_AUDIENCE,
                issuer=jwt_settings.JWT_ISSUER
            )
            
            if payload.get("type") != token_type:
                return None
                
            return payload
        except JWTError as e:
            auth_logger.error(f"令牌验证失败: {str(e)}")
            return None

    def store_verification_code(self, email: str, code: str) -> None:
        """
        存储验证码
        
        Args:
            email: 用户邮箱
            code: 验证码
        """
        try:
            key = f"verification_code:{email}"
            self.redis.setex(key, settings.CAPTCHA_EXPIRE_SECONDS, code)
            auth_logger.info(f"验证码已存储，将在{settings.CAPTCHA_EXPIRE_SECONDS}秒后过期")
        except redis.RedisError as e:
            auth_logger.error(f"存储验证码时发生错误: {str(e)}")
            raise

    def verify_code(self, email: str, code: str) -> bool:
        """
        验证验证码
        
        Args:
            email: 用户邮箱
            code: 验证码
            
        Returns:
            bool: 验证码正确返回True，否则返回False
        """
        try:
            key = f"verification_code:{email}"
            stored_code = self.redis.get(key)
            if stored_code and stored_code == code:
                self.redis.delete(key)  # 验证成功后删除验证码
                return True
            return False
        except redis.RedisError as e:
            auth_logger.error(f"验证验证码时发生错误: {str(e)}")
            return False

    def authenticate_user(
        self,
        username: str,
        password: str,
        captcha_id: str,
        captcha_text: str
    ) -> Optional[User]:
        """验证用户
        
        Args:
            username: 用户名
            password: 密码
            captcha_id: 验证码ID
            captcha_text: 验证码文本
            
        Returns:
            Optional[User]: 验证通过返回用户对象，否则返回None
            
        Raises:
            HTTPException: 验证失败时抛出异常
        """
        try:
            # 验证验证码
            auth_logger.info(f"开始验证 - 用户名: {username}")
            auth_logger.debug(f"验证码信息 - ID: {captcha_id}, 文本: {captcha_text}")
            
            if not self.captcha_manager.verify_captcha_sync(captcha_id, captcha_text):
                auth_logger.warning(f"验证码验证失败 - 用户名: {username}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="验证码错误或已过期"
                )
            
            # 获取用户
            user = self.user_service.get_user_by_username(username)
            if not user:
                auth_logger.warning(f"用户不存在 - 用户名: {username}")
                self._record_login_attempt(None, False, "用户不存在")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码错误"
                )
            
            # 检查账户锁定状态
            if user.locked_until and user.locked_until > datetime.utcnow():
                remaining_time = (user.locked_until - datetime.utcnow()).total_seconds() / 60
                auth_logger.warning(f"账户已锁定 - 用户名: {username}, 剩余时间: {remaining_time:.1f}分钟")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"账户已锁定，请{remaining_time:.1f}分钟后重试"
                )
            
            # 验证密码
            if not self.verify_password(password, user.password_hash):
                auth_logger.warning(f"密码验证失败 - 用户名: {username}")
                self._record_login_attempt(user, False, "密码错误")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码错误"
                )
            
            # 验证成功
            auth_logger.info(f"验证成功 - 用户名: {username}")
            self._record_login_attempt(user, True, "登录成功")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            auth_logger.error(f"验证过程发生错误: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="验证过程发生错误"
            )

    def _record_login_attempt(self, user: User, success: bool, message: str):
        """记录登录尝试
        
        Args:
            user (User): 用户对象
            success (bool): 是否成功
            message (str): 状态消息
        """
        try:
            # 创建登录日志记录
            login_log = LoginLog(
                user_id=user.id,
                username=user.username,
                login_time=datetime.utcnow(),
                login_ip=None,  # 在路由层设置
                user_agent=None,  # 在路由层设置
                login_status=success,
                status_message=message
            )
            
            # 添加到会话
            self.db.add(login_log)
            
            # 如果登录失败，增加失败计数
            if not success:
                user.login_attempts = (user.login_attempts or 0) + 1
                # 如果失败次数超过限制，锁定账户
                if user.login_attempts >= self._max_login_attempts:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=self._lockout_duration)
                    user.is_active = False
                    auth_logger.warning(f"用户账户已锁定: {user.username}, 失败次数: {user.login_attempts}")
            else:
                # 登录成功，重置失败计数
                user.login_attempts = 0
                user.locked_until = None
                
            # 提交事务
            try:
                self.db.commit()
                auth_logger.info(f"登录日志记录成功: {user.username}, 状态: {'成功' if success else '失败'}")
            except Exception as e:
                self.db.rollback()
                auth_logger.error(f"提交登录日志失败: {str(e)}")
                raise
            
        except Exception as e:
            auth_logger.error(f"记录登录尝试失败: {str(e)}")
            self.db.rollback()
            # 不抛出异常，避免影响主流程

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        刷新访问令牌
        
        参数:
            - refresh_token: 刷新令牌
            
        返回:
            - TokenResponse: 新的令牌响应对象
        """
        try:
            # 验证刷新令牌
            payload = self.verify_token(refresh_token, token_type="refresh")
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的刷新令牌"
                )
            
            # 获取用户
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的刷新令牌"
                )
            
            user = self.user_service.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在或已禁用"
                )
            
            # 创建新令牌
            return self.create_tokens(user)
            
        except HTTPException:
            raise
        except Exception as e:
            auth_logger.error(f"刷新令牌失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="令牌刷新失败"
            )

    def revoke_token(self, token: str) -> bool:
        """撤销令牌
        
        Args:
            token (str): 要撤销的令牌
            
        Returns:
            bool: 撤销是否成功
        """
        try:
            # 将令牌添加到Redis黑名单
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            exp = payload.get("exp")
            if exp:
                # 计算剩余过期时间
                ttl = exp - datetime.utcnow().timestamp()
                if ttl > 0:
                    self.redis.setex(f"revoked_token:{token}", int(ttl), "1")
                    auth_logger.info(f"成功撤销令牌: {token[:10]}...")
                    return True
            return False
        except Exception as e:
            auth_logger.error(f"撤销令牌失败: {str(e)}")
            return False

    def _is_token_revoked(self, token: str) -> bool:
        """检查令牌是否被撤销
        
        Args:
            token (str): JWT令牌
            
        Returns:
            bool: 是否被撤销
        """
        return bool(self.redis.get(f"revoked_token:{token}"))

    def get_current_user(self, token: str) -> Optional[User]:
        """获取当前用户
        
        Args:
            token (str): JWT令牌
            
        Returns:
            Optional[User]: 用户对象
            
        Raises:
            HTTPException: 认证失败
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        payload = self.verify_token(token, token_type="access")
        if not payload:
            raise credentials_exception
            
        username: str = payload.get("sub")
        if username is None:
            auth_logger.warning("令牌中缺少用户名")
            raise credentials_exception
            
        user = self.user_service.get_user_by_username(username=username)
        if user is None:
            auth_logger.warning(f"找不到令牌对应的用户: {username}")
            raise credentials_exception
            
        auth_logger.info(f"成功获取当前用户: {username}")
        return user

    def generate_captcha(self) -> dict:
        """同步生成验证码
        
        Returns:
            dict: 包含验证码ID、图片base64和过期时间
            
        Raises:
            HTTPException: 验证码生成失败时抛出异常
        """
        try:
            # 确保Redis连接有效
            if not check_redis_alive(self.redis):
                self.redis = get_redis()
                self.cache_manager = get_cache_manager()
                self.captcha_manager = get_captcha_manager()
            
            # 使用验证码管理器生成验证码
            result = self.captcha_manager.generate_captcha()
            auth_logger.info(f"验证码生成成功 - ID: {result['captcha_id']}")
            return result
        except Exception as e:
            auth_logger.error(f"生成验证码失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"生成验证码失败: {str(e)}"
            )

# 创建认证服务实例
auth_service = AuthService() 