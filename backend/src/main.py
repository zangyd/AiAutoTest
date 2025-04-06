from fastapi import FastAPI, HTTPException, Request, Form, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import logging
from datetime import datetime, timedelta
from jose import jwt
from starlette.middleware.sessions import SessionMiddleware

from api.base import api_router
from api.deps import get_current_user
from api.models import UserOut
from core.config.jwt_config import jwt_settings
from core.auth.jwt import jwt_handler

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="测试平台",
    description="自动化测试平台API",
    version="1.0.0"
)

# 添加会话中间件
app.add_middleware(SessionMiddleware, secret_key=jwt_settings.SECRET_KEY)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置模板目录
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# 用户认证相关模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 模拟用户数据
users_db = {
    "admin": {
        "username": "admin",
        "password": "admin",
        "email": "admin@example.com",
        "permissions": ["admin", "user_view", "user_manage"]
    }
}

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

@app.post("/api/v1/auth/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = users_db[form_data.username]
    if user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = jwt_handler.create_token(
        data={"sub": user["username"]},
        expires_delta=jwt_settings.access_token_expires
    )
    return {"access_token": access_token, "token_type": jwt_settings.TOKEN_TYPE}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: UserOut = Depends(get_current_user)):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": current_user}
    )

# 包含API路由
app.include_router(api_router) 