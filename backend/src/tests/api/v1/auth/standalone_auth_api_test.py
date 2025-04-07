#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立的认证API测试脚本
测试认证API的各个接口，包括:
- 生成验证码
- 用户登录
- 令牌刷新
- 用户登出
- 获取当前用户信息

此脚本可以独立运行，不依赖于conftest.py
"""
import asyncio
import json
import base64
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# 添加项目根目录到Python路径
backend_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

import jwt
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel

# 模拟数据和工具函数
class MockUser:
    """模拟用户对象"""
    def __init__(self, id=1, username="testuser", email="test@example.com"):
        self.id = id
        self.username = username
        self.email = email
        self.phone = "13800138000"
        self.is_active = True
        self.is_superuser = False
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_login = datetime.now()
        self.hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # 等同于"password"

class MockDB:
    """模拟数据库会话"""
    def __init__(self):
        self.users = {
            1: MockUser(id=1, username="testuser", email="test@example.com")
        }
    
    def query(self, model):
        """模拟查询方法"""
        return MockQuery(self.users)

class MockQuery:
    """模拟查询对象"""
    def __init__(self, data):
        self.data = data
        
    def filter(self, *args, **kwargs):
        """模拟过滤方法"""
        return self
        
    def first(self):
        """模拟获取第一个结果"""
        if self.data:
            return list(self.data.values())[0]
        return None

class MockRedis:
    """模拟Redis客户端"""
    def __init__(self):
        self.data = {}
        
    async def get(self, key):
        """模拟获取数据"""
        return self.data.get(key)
        
    async def set(self, key, value, ex=None):
        """模拟设置数据"""
        self.data[key] = value
        
    async def exists(self, key):
        """模拟检查键是否存在"""
        return key in self.data
        
    async def delete(self, key):
        """模拟删除键"""
        if key in self.data:
            del self.data[key]
            return 1
        return 0

class MockCaptchaManager:
    """模拟验证码管理器"""
    def __init__(self):
        self.captchas = {}
        
    async def generate_captcha(self):
        """生成模拟验证码"""
        captcha_id = "test-captcha-id"
        captcha_text = "ABCD"
        captcha_image = "data:image/png;base64,..."
        
        # 存储验证码，使其可以被验证
        self.captchas[captcha_id] = captcha_text
        print(f"生成验证码: ID={captcha_id}, 文本={captcha_text}")
        
        return {
            "captcha_id": captcha_id,
            "captcha_image": captcha_image,
            "expire_in": 300
        }
        
    async def verify_captcha(self, captcha_id, captcha_text):
        """验证验证码"""
        if not captcha_id or not captcha_text:
            print(f"验证码验证失败: ID或文本为空")
            return False
            
        stored_text = self.captchas.get(captcha_id)
        if not stored_text:
            print(f"验证码验证失败: 找不到ID={captcha_id}的验证码")
            return False
        
        print(f"验证码比较: 存储的={stored_text}, 输入的={captcha_text}")    
        result = stored_text.lower() == captcha_text.lower()
        if result:
            # 验证成功后删除验证码，确保一次性使用
            del self.captchas[captcha_id]
            print(f"验证码验证成功: ID={captcha_id}")
        else:
            print(f"验证码验证失败: 不匹配")
            
        return result

class MockAuthService:
    """模拟认证服务"""
    def __init__(self):
        self.db = MockDB()
        self.redis = MockRedis()
        self.captcha_manager = MockCaptchaManager()
        self.token_blacklist = MockTokenBlacklist()
        
    async def authenticate_user(self, username, password, captcha_id=None, captcha_text=None, ip_address=None, user_agent=None):
        """模拟用户认证"""
        # 验证验证码
        if captcha_id and captcha_text:
            captcha_valid = await self.captcha_manager.verify_captcha(captcha_id, captcha_text)
            if not captcha_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="验证码错误或已过期"
                )
        
        # 查询用户
        user = None
        for u in self.db.users.values():
            if u.username == username:
                user = u
                break
                
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
            
        # 模拟密码验证 - 在实际中会使用password.verify_password
        if password != "password":  # 简化密码验证
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已被禁用"
            )
            
        return user
    
    async def create_tokens(self, user_id, username):
        """创建访问令牌和刷新令牌"""
        access_token_expires = timedelta(minutes=30)
        refresh_token_expires = timedelta(days=7)
        
        # 创建访问令牌
        access_token_data = {
            "sub": str(user_id),
            "username": username,
            "exp": datetime.utcnow() + access_token_expires
        }
        access_token = self._create_token(access_token_data)
        
        # 创建刷新令牌
        refresh_token_data = {
            "sub": str(user_id),
            "username": username,
            "exp": datetime.utcnow() + refresh_token_expires,
            "token_type": "refresh"
        }
        refresh_token = self._create_token(refresh_token_data)
        
        return access_token, refresh_token
    
    def _create_token(self, data):
        """创建JWT令牌"""
        secret_key = "test_secret_key"
        algorithm = "HS256"
        return jwt.encode(data, secret_key, algorithm=algorithm)
    
    async def refresh_access_token(self, refresh_token):
        """刷新访问令牌"""
        try:
            # 验证刷新令牌
            secret_key = "test_secret_key"
            algorithm = "HS256"
            payload = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
            
            # 检查令牌类型
            if payload.get("token_type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的刷新令牌"
                )
                
            # 检查令牌是否在黑名单中
            token_in_blacklist = await self.token_blacklist.is_blacklisted(refresh_token)
            if token_in_blacklist:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="令牌已被撤销"
                )
                
            # 创建新的访问令牌
            user_id = payload.get("sub")
            username = payload.get("username")
            
            access_token_expires = timedelta(minutes=30)
            access_token_data = {
                "sub": user_id,
                "username": username,
                "exp": datetime.utcnow() + access_token_expires,
                # 添加一个随机字段，确保每次生成的令牌都不同
                "nonce": datetime.utcnow().timestamp()
            }
            
            # 创建新的访问令牌
            new_access_token = self._create_token(access_token_data)
            
            return new_access_token
            
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
    
    async def logout(self, token):
        """用户登出，将令牌加入黑名单"""
        if not token:
            return False
            
        # 将令牌加入黑名单
        success = await self.token_blacklist.add_to_blacklist(token)
        return success

class MockTokenBlacklist:
    """模拟令牌黑名单"""
    def __init__(self):
        self.blacklist = set()
        
    async def add_to_blacklist(self, token):
        """将令牌加入黑名单"""
        if not token:
            return False
            
        try:
            # 验证令牌
            secret_key = "test_secret_key"
            algorithm = "HS256"
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            
            # 将令牌添加到黑名单
            self.blacklist.add(token)
            return True
            
        except jwt.PyJWTError:
            # 无效令牌
            return False
    
    async def is_blacklisted(self, token):
        """检查令牌是否在黑名单中"""
        if not token:
            return False
            
        return token in self.blacklist

# 创建模拟FastAPI应用
def create_test_app():
    """创建测试应用"""
    # 创建应用
    app = FastAPI()
    
    # 创建全局的验证码管理器、令牌黑名单和认证服务，使数据在不同请求之间共享
    captcha_manager = MockCaptchaManager()
    token_blacklist = MockTokenBlacklist()
    auth_service = MockAuthService()
    auth_service.captcha_manager = captcha_manager
    auth_service.token_blacklist = token_blacklist
    
    # 获取当前用户
    async def get_current_user(authorization: str = None):
        """获取当前用户"""
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证信息",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        token = authorization.replace("Bearer ", "")
        
        try:
            # 验证令牌
            secret_key = "test_secret_key"
            algorithm = "HS256"
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            
            # 检查令牌是否在黑名单中
            is_blacklisted = await token_blacklist.is_blacklisted(token)
            print(f"令牌黑名单检查: {token} -> {'已拉黑' if is_blacklisted else '未拉黑'}")
            if is_blacklisted:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="令牌已被撤销",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            # 获取用户ID
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的认证信息",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            # 查询用户
            db = MockDB()
            user = db.users.get(int(user_id))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            # 检查用户状态
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户已被禁用"
                )
                
            return user
            
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证信息",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    # 定义路由
    @app.post("/api/v1/auth/captcha")
    async def generate_captcha():
        """生成验证码"""
        return await captcha_manager.generate_captcha()
    
    # 使用Pydantic模型定义请求体
    class LoginRequest(BaseModel):
        username: str
        password: str
        captcha_id: str = None
        captcha_text: str = None
    
    @app.post("/api/v1/auth/login")
    async def login(request: LoginRequest):
        """用户登录"""
        # 使用全局的auth_service
        
        # 验证用户凭据
        user = await auth_service.authenticate_user(
            username=request.username,
            password=request.password,
            captcha_id=request.captcha_id,
            captcha_text=request.captcha_text
        )
        
        # 创建令牌
        access_token, refresh_token = await auth_service.create_tokens(user.id, user.username)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800  # 30分钟
        }
    
    class RefreshTokenRequest(BaseModel):
        refresh_token: str
    
    @app.post("/api/v1/auth/refresh")
    async def refresh_token(request: RefreshTokenRequest):
        """刷新令牌"""
        # 使用全局的auth_service
        
        # 刷新令牌
        access_token = await auth_service.refresh_access_token(request.refresh_token)
        
        return {
            "access_token": access_token,
            "refresh_token": request.refresh_token,
            "token_type": "bearer",
            "expires_in": 1800  # 30分钟
        }
    
    class LogoutRequest(BaseModel):
        token: str
        refresh_token: str = None
    
    @app.post("/api/v1/auth/logout")
    async def logout(request: LogoutRequest):
        """用户登出"""
        # 使用全局的auth_service
        
        # 将令牌加入黑名单
        success = await auth_service.logout(request.token)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="登出失败"
            )
        
        # 如果提供了刷新令牌，也将其加入黑名单
        if request.refresh_token:
            await auth_service.logout(request.refresh_token)
        
        return {"success": True}
    
    @app.get("/api/v1/auth/me")
    async def get_current_user_info(request: Request):
        """获取当前用户信息"""
        # 从请求头中获取Authorization
        authorization = request.headers.get("Authorization")
        print(f"获取到的Authorization头: {authorization}")
        
        user = await get_current_user(authorization)
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "last_login": user.last_login.isoformat()
        }
    
    return app

# 测试函数
async def test_auth_api():
    """测试认证API"""
    # 创建测试应用
    app = create_test_app()
    client = TestClient(app)
    
    print("\n=== 测试认证API ===")
    
    # 1. 测试生成验证码
    print("测试生成验证码...")
    captcha_response = client.post("/api/v1/auth/captcha")
    assert captcha_response.status_code == 200
    captcha_data = captcha_response.json()
    assert "captcha_id" in captcha_data
    assert "captcha_image" in captcha_data
    captcha_id = captcha_data["captcha_id"]
    print("✓ 验证码生成测试通过")
    
    # 2. 测试登录成功
    print("测试登录成功...")
    login_data = {
        "username": "testuser",
        "password": "password",
        "captcha_id": captcha_id,
        "captcha_text": "ABCD"  # 使用模拟验证码的值
    }
    try:
        login_response = client.post("/api/v1/auth/login", json=login_data)
        print(f"登录响应状态码: {login_response.status_code}")
        print(f"登录响应内容: {login_response.text}")
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        print("✓ 登录成功测试通过")
    except Exception as e:
        print(f"登录测试失败: {str(e)}")
        print(f"请求数据: {login_data}")
        raise
    
    # 3. 测试获取当前用户信息
    print("测试获取当前用户信息...")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        user_response = client.get("/api/v1/auth/me", headers=headers)
        print(f"用户信息响应状态码: {user_response.status_code}")
        print(f"用户信息响应内容: {user_response.text}")
        assert user_response.status_code == 200
        user_data = user_response.json()
        assert user_data["username"] == "testuser"
        assert user_data["email"] == "test@example.com"
        print("✓ 获取当前用户信息测试通过")
    except Exception as e:
        print(f"获取用户信息测试失败: {str(e)}")
        raise
    
    # 4. 测试刷新令牌
    print("测试刷新令牌...")
    refresh_data = {"refresh_token": refresh_token}
    try:
        refresh_response = client.post("/api/v1/auth/refresh", json=refresh_data)
        print(f"刷新令牌响应状态码: {refresh_response.status_code}")
        print(f"刷新令牌响应内容: {refresh_response.text}")
        assert refresh_response.status_code == 200
        new_token_data = refresh_response.json()
        assert "access_token" in new_token_data
        new_access_token = new_token_data["access_token"]
        assert new_access_token != access_token
        print("✓ 刷新令牌测试通过")
    except Exception as e:
        print(f"刷新令牌测试失败: {str(e)}")
        raise
    
    # 5. 测试用户登出
    print("测试用户登出...")
    logout_data = {
        "token": access_token,
        "refresh_token": refresh_token
    }
    try:
        logout_response = client.post("/api/v1/auth/logout", json=logout_data)
        print(f"登出响应状态码: {logout_response.status_code}")
        print(f"登出响应内容: {logout_response.text}")
        assert logout_response.status_code == 200
        print("✓ 用户登出测试通过")
    except Exception as e:
        print(f"登出测试失败: {str(e)}")
        raise
    
    # 6. 测试登出后无法访问受保护的资源
    print("测试登出后无法访问受保护的资源...")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        user_response = client.get("/api/v1/auth/me", headers=headers)
        print(f"登出后访问响应状态码: {user_response.status_code}")
        print(f"登出后访问响应内容: {user_response.text}")
        assert user_response.status_code == 401
        print("✓ 登出后的令牌无效测试通过")
    except Exception as e:
        print(f"登出后访问测试失败: {str(e)}")
        raise
    
    # 7. 测试登录失败 - 错误的用户名或密码
    print("测试登录失败 - 错误的用户名或密码...")
    # 先获取新的验证码
    captcha_response = client.post("/api/v1/auth/captcha")
    captcha_data = captcha_response.json()
    captcha_id = captcha_data["captcha_id"]
    
    login_data = {
        "username": "testuser",
        "password": "wrong_password",
        "captcha_id": captcha_id,
        "captcha_text": "ABCD"
    }
    try:
        login_response = client.post("/api/v1/auth/login", json=login_data)
        print(f"错误密码登录响应状态码: {login_response.status_code}")
        print(f"错误密码登录响应内容: {login_response.text}")
        assert login_response.status_code == 401
        print("✓ 登录失败测试通过")
    except Exception as e:
        print(f"登录失败测试失败: {str(e)}")
        raise
    
    # 8. 测试登录失败 - 验证码错误
    print("测试登录失败 - 验证码错误...")
    # 先获取新的验证码
    captcha_response = client.post("/api/v1/auth/captcha")
    captcha_data = captcha_response.json()
    captcha_id = captcha_data["captcha_id"]
    
    login_data = {
        "username": "testuser",
        "password": "password",
        "captcha_id": captcha_id,
        "captcha_text": "WRONG"
    }
    try:
        login_response = client.post("/api/v1/auth/login", json=login_data)
        print(f"错误验证码登录响应状态码: {login_response.status_code}")
        print(f"错误验证码登录响应内容: {login_response.text}")
        assert login_response.status_code == 400
        print("✓ 验证码错误测试通过")
    except Exception as e:
        print(f"验证码错误测试失败: {str(e)}")
        raise
    
    print("\n✓✓✓ 所有认证API测试通过! ✓✓✓")

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_auth_api()) 