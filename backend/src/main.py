from fastapi import FastAPI, HTTPException, Request, Form, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import logging
from datetime import datetime, timedelta
from jose import jwt
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import redis

from api import api_router
from api.core.auth import get_current_user
from core.auth.schemas import UserOut, CaptchaResponse, TokenResponse
from core.config.jwt_config import jwt_settings
from core.config.settings import settings
from core.auth.jwt import create_access_token
from core.logging import LoggingMiddleware
from core.database import get_db
from core.database.redis import get_redis
from core.auth.service import AuthService
from core.auth.captcha import CaptchaManager
from core.auth.models import User

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_critical_configs():
    """验证关键配置项，确保生产环境中不使用不安全的默认值"""
    if settings.ENV == "production":
        # 检查JWT密钥是否已设置且不是默认值
        if not settings.JWT_SECRET_KEY or settings.JWT_SECRET_KEY == "请在环境变量或.env文件中设置此值":
            logger.critical("生产环境必须设置强JWT SECRET KEY")
            raise RuntimeError("生产环境必须设置强JWT SECRET KEY")
        
        # 检查应用密钥是否已设置且不是默认值
        if not settings.SECRET_KEY or settings.SECRET_KEY == "请在环境变量或.env文件中设置此值":
            logger.critical("生产环境必须设置强SECRET KEY")
            raise RuntimeError("生产环境必须设置强SECRET KEY")
        
        # 检查数据库密码是否已设置
        if not settings.MYSQL_PASSWORD:
            logger.warning("生产环境中数据库密码为空，这可能存在安全风险")
        
        # 检查Redis密码是否已设置（如果使用）
        if settings.REDIS_HOST and settings.REDIS_PORT and not settings.REDIS_PASSWORD:
            logger.warning("生产环境中Redis未设置密码，这可能存在安全风险")
        
        # 检查允许的主机是否限制了
        if "*" in settings.ALLOWED_HOSTS:
            logger.warning("生产环境中ALLOWED_HOSTS包含'*'，应该限制为特定域名")
    
    logger.info(f"当前运行环境: {settings.ENV}")

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """获取认证服务实例
    
    Args:
        db (Session): 数据库会话实例
        
    Returns:
        AuthService: 认证服务实例
    """
    return AuthService(db=db)

def create_app() -> FastAPI:
    """
    创建FastAPI应用实例
    
    Returns:
        FastAPI: 应用实例
    """
    # 验证关键配置
    validate_critical_configs()
    
    app = FastAPI(
        title="测试平台",
        description="自动化测试平台API",
        version="1.0.0"
    )
    
    # 添加会话中间件
    app.add_middleware(SessionMiddleware, secret_key=jwt_settings.JWT_SECRET_KEY)

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 添加日志中间件
    app.add_middleware(LoggingMiddleware)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        try:
            logger.info(f"Request: {request.method} {request.url}")
            response = await call_next(request)
            logger.info(f"Response Status: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"message": "Internal server error"}
            )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error"}
        )

    @app.post("/api/v1/auth/login", response_model=TokenResponse)
    async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        captcha_id: str = Form(...),
        captcha_text: str = Form(...),
        auth_service: AuthService = Depends(get_auth_service)
    ):
        """用户登录
        
        Args:
            form_data: 登录表单数据
            captcha_id: 验证码ID
            captcha_text: 验证码文本
            auth_service: 认证服务实例
            
        Returns:
            TokenResponse: 包含访问令牌和刷新令牌的响应
            
        Raises:
            HTTPException: 登录失败时抛出异常
        """
        try:
            # 验证用户
            user = auth_service.authenticate_user(
                username=form_data.username,
                password=form_data.password,
                captcha_id=captcha_id,
                captcha_text=captcha_text
            )

            # 生成令牌
            tokens = auth_service.create_tokens(user)
            return tokens

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    @app.get("/")
    async def read_root():
        """API根路由
        
        Returns:
            dict: API状态信息
        """
        return {
            "status": "ok",
            "message": "自动化测试平台API服务正在运行",
            "version": "1.0.0",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        }

    # 包含API路由
    app.include_router(api_router, prefix="/api")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 