from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from typing import Optional
import os
import logging
from starlette.middleware.sessions import SessionMiddleware

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="测试平台")

# 添加会话中间件
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

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
class User(BaseModel):
    username: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

# 模拟用户数据
users_db = {
    "admin": {
        "username": "admin",
        "password": "admin",
        "email": "admin@example.com"
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username not in users_db:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    user = users_db[username]
    if user["password"] != password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 设置会话
    request.session["user"] = username
    logger.info(f"User {username} logged in successfully")
    
    response = RedirectResponse(url="/dashboard", status_code=302)
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    # 从会话中获取用户信息
    username = request.session.get("user")
    if not username:
        logger.warning("Unauthorized access attempt to dashboard")
        return RedirectResponse(url="/login", status_code=302)
    
    user = users_db[username]
    logger.info(f"User {username} accessed dashboard")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user}) 