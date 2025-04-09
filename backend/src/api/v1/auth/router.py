"""
认证相关API接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging
import os
from datetime import timedelta, datetime

from core.database import get_db
from core.auth.service import AuthService, auth_logger
from core.auth.schemas import (
    Token, TokenResponse, RefreshToken, 
    LogoutRequest, UserOut, CaptchaResponse
)
from .schemas import UserResponse, LoginLog
from core.config import settings
from core.config.jwt_config import jwt_settings
from core.auth.dependencies import get_current_user

# 配置日志
logger = logging.getLogger("auth_router")
logger.setLevel(logging.DEBUG)

# 创建日志目录
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "logs"))
os.makedirs(log_dir, exist_ok=True)

# 创建文件处理器
log_file = os.path.join(log_dir, "auth_router.log")
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 移除现有的处理器（避免重复）
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# 添加处理器到日志记录器
logger.addHandler(file_handler)

# 测试日志记录
logger.debug(f"auth_router日志初始化完成 - 日志文件路径: {log_file}")

router = APIRouter(prefix="/auth", tags=["认证"])

# 创建OAuth2密码承载器
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    captcha_id: str = Form(...),
    captcha_text: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    
    参数:
        - username: 用户名
        - password: 密码
        - captcha_id: 验证码ID
        - captcha_text: 验证码文本
        
    返回:
        - access_token: 访问令牌
        - refresh_token: 刷新令牌
        - token_type: 令牌类型
        - expires_in: 访问令牌过期时间(秒)
    """
    try:
        # 创建认证服务实例
        auth_service = AuthService(db)
        
        # 获取客户端信息
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # 记录登录尝试
        logger.info(f"登录尝试 - 用户名: {username}, IP: {client_host}, User-Agent: {user_agent}")
        logger.info(f"验证码信息 - ID: {captcha_id}, 文本: {captcha_text}")
        
        # 验证用户
        user = auth_service.authenticate_user(
            username=username,
            password=password,
            captcha_id=captcha_id,
            captcha_text=captcha_text
        )
        
        if not user:
            logger.warning(f"用户验证失败 - 用户名: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 检查用户状态
        if not user.is_active:
            logger.warning(f"用户已禁用 - 用户名: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已被禁用"
            )
            
        # 检查账户锁定状态
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining_time = (user.locked_until - datetime.utcnow()).total_seconds() / 60
            logger.warning(f"账户已锁定 - 用户名: {username}, 剩余锁定时间: {remaining_time:.1f}分钟")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"账户已锁定，请在{remaining_time:.1f}分钟后重试"
            )
        
        # 生成令牌
        tokens = auth_service.create_tokens(user)
        
        # 更新用户最后登录信息
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = client_host
        user.login_attempts = 0  # 重置登录尝试次数
        user.locked_until = None  # 清除锁定时间
        
        # 创建登录日志
        login_log = LoginLog(
            user_id=user.id,
            username=user.username,
            login_time=datetime.utcnow(),
            login_ip=client_host,
            user_agent=user_agent,
            login_status=True,
            status_message="登录成功"
        )
        db.add(login_log)
        
        try:
            db.commit()
            logger.info(f"登录成功 - 用户名: {user.username}, IP: {client_host}")
        except Exception as e:
            db.rollback()
            logger.error(f"保存登录记录失败: {str(e)}")
            # 继续处理，不影响用户登录
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        if "Multiple classes found for path" in str(e):
            # 数据库模型冲突错误
            logger.error("数据库模型定义冲突，请检查模型导入")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="数据库模型定义冲突"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: RefreshToken,
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌
    
    参数:
        - refresh_token: 刷新令牌
        
    返回:
        - 新的令牌对
    """
    auth_service = AuthService(db)
    new_tokens = auth_service.refresh_access_token(refresh_token.refresh_token)
    
    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return new_tokens

@router.post("/logout")
async def logout(
    logout_request: LogoutRequest,
    db: Session = Depends(get_db)
):
    """
    用户登出
    
    参数:
        - token: 要撤销的访问令牌
        - refresh_token: 要撤销的刷新令牌（可选）
    """
    auth_service = AuthService(db)
    auth_service.revoke_token(logout_request.token)
    
    if logout_request.refresh_token:
        auth_service.revoke_token(logout_request.refresh_token)
    
    return {"detail": "登出成功"}

@router.get("/me", response_model=UserOut)
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息
    
    参数:
        - token: 访问令牌（从请求头获取）
        
    返回:
        - 当前用户信息
    """
    auth_service = AuthService(db)
    current_user = auth_service.get_current_user(token)
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user

@router.post("/captcha", response_model=CaptchaResponse)
def generate_captcha(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    生成验证码
    
    返回:
        - captcha_id: 验证码ID
        - captcha_image: 验证码图片的base64编码
        - expire_in: 验证码过期时间(秒)
    """
    try:
        auth_service = AuthService(db)
        logger.debug("开始生成验证码")
        result = auth_service.generate_captcha()
        return result
    except Exception as e:
        logger.error(f"生成验证码失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成验证码失败: {str(e)}"
        )

@router.get("/user-info", response_model=UserResponse)
async def get_user_info(current_user = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        real_name=current_user.real_name,
        position=current_user.position,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        locked_until=current_user.locked_until,
        password_changed_at=current_user.password_changed_at,
        last_login_at=current_user.last_login_at,
        last_login_ip=current_user.last_login_ip,
        login_attempts=current_user.login_attempts,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        created_by=current_user.created_by,
        updated_by=current_user.updated_by,
        roles=current_user.roles,
        departments=current_user.departments
    )
