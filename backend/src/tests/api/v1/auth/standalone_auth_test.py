"""独立的认证API测试脚本"""
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock, MagicMock

# 添加项目根目录到Python路径
backend_path = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

# 设置测试环境变量
os.environ["ENV"] = "test"
os.environ["TESTING"] = "True"
os.environ["JWT_SECRET_KEY"] = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
os.environ["JWT_ALGORITHM"] = "HS256"

# 导入必要的模块
from fastapi import FastAPI
from httpx import AsyncClient

# 延迟导入，确保环境变量已设置
from api.v1.auth.router import router as auth_router
from core.auth.schemas import UserOut, TokenData

# 创建测试应用
def create_test_app():
    """创建测试应用"""
    app = FastAPI()
    app.include_router(auth_router, prefix="/api/v1/auth")
    return app

# 创建测试用户
def create_mock_user():
    """创建测试用户"""
    return UserOut(
        id=1,
        username="testuser",
        email="test@example.com",
        phone="13800138000",
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        last_login=datetime.now()
    )

# 创建测试令牌
def create_test_token():
    """创建测试令牌"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJ0ZXN0dXNlciJ9.signature"

# 测试登录成功
async def test_login_success():
    """测试登录成功"""
    # 准备数据
    mock_user = create_mock_user()
    app = create_test_app()
    login_data = {"username": "testuser", "password": "password"}
    
    # 模拟认证服务
    async def mock_authenticate_user(username, password):
        if username == "testuser" and password == "password":
            return mock_user
        raise ValueError("Invalid credentials")
    
    # 应用patch
    with patch("core.auth.service.AuthService.authenticate_user", mock_authenticate_user):
        # 发送请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json=login_data)
        
        # 验证结果
        assert response.status_code == 200, f"预期状态码200，实际为{response.status_code}"
        data = response.json()
        assert "access_token" in data, "响应中缺少access_token"
        assert "refresh_token" in data, "响应中缺少refresh_token"
        assert "token_type" in data, "响应中缺少token_type"
        assert data["token_type"] == "bearer", f"token_type应为bearer，实际为{data['token_type']}"
    
    print("✅ test_login_success 通过")

# 测试登录失败
async def test_login_invalid_credentials():
    """测试登录失败 - 无效凭证"""
    # 准备数据
    app = create_test_app()
    login_data = {"username": "testuser", "password": "wrong_password"}
    
    # 模拟认证服务
    async def mock_authenticate_user(username, password):
        raise ValueError("Invalid credentials")
    
    # 应用patch
    with patch("core.auth.service.AuthService.authenticate_user", mock_authenticate_user):
        # 发送请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json=login_data)
        
        # 验证结果
        assert response.status_code == 401, f"预期状态码401，实际为{response.status_code}"
        data = response.json()
        assert "detail" in data, "响应中缺少detail"
    
    print("✅ test_login_invalid_credentials 通过")

# 测试登出
async def test_logout():
    """测试登出"""
    # 准备数据
    app = create_test_app()
    user_token = create_test_token()
    
    # 模拟依赖函数
    def mock_verify_token(token):
        return TokenData(sub="1", username="testuser")
    
    async def mock_get_current_user():
        return create_mock_user()
    
    # 模拟黑名单
    mock_blacklist = AsyncMock()
    mock_blacklist.add_to_blacklist.return_value = True
    
    # 应用patch
    with patch("core.auth.jwt.verify_token", mock_verify_token), \
         patch("api.v1.auth.router.get_current_user", mock_get_current_user), \
         patch("api.v1.auth.router.token_blacklist", mock_blacklist):
        
        # 发送请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/logout",
                headers={"Authorization": f"Bearer {user_token}"}
            )
        
        # 验证结果
        assert response.status_code == 200, f"预期状态码200，实际为{response.status_code}"
        mock_blacklist.add_to_blacklist.assert_called_once()
        data = response.json()
        assert "message" in data, "响应中缺少message"
        assert "success" in data["message"].lower(), f"message应包含success，实际为{data['message']}"
    
    print("✅ test_logout 通过")

# 测试获取当前用户信息
async def test_me():
    """测试获取当前用户信息"""
    # 准备数据
    app = create_test_app()
    user_token = create_test_token()
    mock_user = create_mock_user()
    
    # 模拟依赖函数
    def mock_verify_token(token):
        return TokenData(sub="1", username="testuser")
    
    async def mock_get_current_user():
        return mock_user
    
    # 应用patch
    with patch("core.auth.jwt.verify_token", mock_verify_token), \
         patch("api.v1.auth.router.get_current_user", mock_get_current_user):
        
        # 发送请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/auth/me", 
                headers={"Authorization": f"Bearer {user_token}"}
            )
        
        # 验证结果
        assert response.status_code == 200, f"预期状态码200，实际为{response.status_code}"
        data = response.json()
        assert data["username"] == mock_user.username, f"username预期为{mock_user.username}，实际为{data['username']}"
        assert data["email"] == mock_user.email, f"email预期为{mock_user.email}，实际为{data['email']}"
    
    print("✅ test_me 通过")

# 测试无效令牌
async def test_invalid_token():
    """测试无效令牌"""
    # 准备数据
    app = create_test_app()
    
    # 模拟认证失败
    def mock_verify_token(token):
        raise ValueError("Invalid token")
    
    # 应用patch
    with patch("core.auth.jwt.verify_token", mock_verify_token):
        # 发送请求
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/auth/me", 
                headers={"Authorization": "Bearer invalid_token"}
            )
        
        # 验证结果
        assert response.status_code == 401, f"预期状态码401，实际为{response.status_code}"
    
    print("✅ test_invalid_token 通过")

# 运行所有测试
async def run_all_tests():
    """运行所有测试"""
    print("开始运行认证API测试...\n")
    
    try:
        await test_login_success()
        await test_login_invalid_credentials()
        await test_logout()
        await test_me()
        await test_invalid_token()
        
        print("\n所有测试通过！")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 